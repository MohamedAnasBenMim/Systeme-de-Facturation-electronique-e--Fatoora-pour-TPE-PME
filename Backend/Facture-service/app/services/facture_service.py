from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from pydantic import ValidationError
from typing import List, Optional
from datetime import date

from app.models.facture import Facture, StatutFacture
from app.models.ligneFacture import LigneFacture
from app.schemas.facture_schema import FactureCreate, FactureUpdate
from app.schemas.ligne_facture_schema import LigneFactureCreate
from app.services.numerotation_service import NumerotationService   
from app.core.http_client import (
    get_client_by_id,
    get_entreprise_by_id,
    get_produit_by_id,
    get_devis_by_id,
)
from app.services.pdf_service import generer_pdf_facture



def _calculer_totaux(lignes_data: list[dict]) -> dict:
    total_ht      = sum(l["quantite"] * l["prix_unitaire"] for l in lignes_data)
    tva           = round(total_ht * 0.19, 3)
    timbre_fiscal = 1.0
    total_ttc     = round(total_ht + tva + timbre_fiscal, 3)
    return {
        "total_ht":      round(total_ht, 3),
        "tva":           tva,
        "timbre_fiscal": timbre_fiscal,
        "total_ttc":     total_ttc,
    }


def _get_or_404(db: Session, facture_id: int) -> Facture:
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(
            status_code=404,
            detail=f"Facture {facture_id} introuvable"
        )
    return facture


# ── CREATE ─────────────────────────────────────────────────────────────

async def create_facture(db: Session, data: FactureCreate, token: str = None) -> Facture:
   

    await get_client_by_id(data.client_id)
    await get_entreprise_by_id(data.entreprise_id)

    
    if data.numero_facture:
        numero = data.numero_facture
    else:
        num_svc = NumerotationService(db)
        numero  = num_svc.generer_numero_facture()

   
    lignes_enrichies = []
    for l in data.lignes:
        produit = await get_produit_by_id(l.product_id, token=token)
        designation = (getattr(l, "description", None) or "").strip() or produit.get("designation", f"Produit #{l.product_id}")
        lignes_enrichies.append({
            "product_id":    l.product_id,
            "designation":   designation,
            "quantite":      l.quantite,
            "prix_unitaire": l.prix_unitaire,
            "montant_ligne": round(l.quantite * l.prix_unitaire, 3),
        })

    
    totaux = _calculer_totaux(lignes_enrichies)

    
    try:
        facture = Facture(
            numero        = numero,
            client_id     = data.client_id,
            entreprise_id = data.entreprise_id,
            date_echeance = data.date_echeance,
            source        = data.source,
            source_id     = data.source_id,
            **totaux,
        )
        db.add(facture)
        db.flush()

        for l in lignes_enrichies:
            db.add(LigneFacture(facture_id=facture.id, **l))

        db.commit()
        db.refresh(facture)
        return facture

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Erreur base de données : numéro de facture déjà utilisé ou contrainte violée. {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur base de données : {str(e)}"
        )


# ── READ ───────────────────────────────────────────────────────────────

def get_all_factures(db: Session) -> list[Facture]:
    return db.query(Facture).all()


def get_facture(db: Session, facture_id: int) -> Facture:
    return _get_or_404(db, facture_id)


async def get_facture_detail(db: Session, facture_id: int) -> dict:
    facture    = _get_or_404(db, facture_id)
    client     = await get_client_by_id(facture.client_id)
    entreprise = await get_entreprise_by_id(facture.entreprise_id)
    return {"facture": facture, "client": client, "entreprise": entreprise}


# ── UPDATE ─────────────────────────────────────────────────────────────

async def update_facture(
    db: Session, facture_id: int, data: FactureUpdate, token: str = None
) -> Facture:

    facture = _get_or_404(db, facture_id)

    if facture.statut != StatutFacture.BROUILLON:
        raise HTTPException(
            status_code=400,
            detail="Seules les factures en statut BROUILLON peuvent être modifiées."
        )

    try:
        if data.date_echeance is not None:
            facture.date_echeance = data.date_echeance
        if data.statut is not None:
            facture.statut = data.statut

        if data.lignes is not None:
            db.query(LigneFacture).filter(
                LigneFacture.facture_id == facture_id
            ).delete()

            lignes_enrichies = []
            for l in data.lignes:
                produit = await get_produit_by_id(l.product_id, token=token)
                lignes_enrichies.append({
                    "product_id":    l.product_id,
                    "designation":   produit.get("designation", f"Produit #{l.product_id}"),
                    "quantite":      l.quantite,
                    "prix_unitaire": l.prix_unitaire,
                    "montant_ligne": round(l.quantite * l.prix_unitaire, 3),
                })

            for l in lignes_enrichies:
                db.add(LigneFacture(facture_id=facture_id, **l))

            # Recalcul des totaux après modification des lignes
            totaux = _calculer_totaux(lignes_enrichies)
            facture.total_ht      = totaux["total_ht"]
            facture.tva           = totaux["tva"]
            facture.timbre_fiscal = totaux["timbre_fiscal"]
            facture.total_ttc     = totaux["total_ttc"]

        db.commit()
        db.refresh(facture)
        return facture

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur base de données : {str(e)}"
        )


# ── DELETE ─────────────────────────────────────────────────────────────

def delete_facture(db: Session, facture_id: int) -> dict:
    facture = _get_or_404(db, facture_id)

    if facture.statut == StatutFacture.PAYEE:
        raise HTTPException(
            status_code=400,
            detail="Une facture PAYÉE ne peut pas être supprimée."
        )

    try:
        db.delete(facture)
        db.commit()
        return {"id": facture_id, "status": "deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur base de données : {str(e)}"
        )


# PDF 

async def generer_et_sauvegarder_pdf(db: Session, facture_id: int) -> str:
    detail     = await get_facture_detail(db, facture_id)
    facture    = detail["facture"]
    client     = detail["client"]
    entreprise = detail["entreprise"]

    pdf_path = generer_pdf_facture(facture, entreprise, client)

    facture.pdf_path = pdf_path
    db.commit()

    return pdf_path


# CRÉATION DEPUIS UN DEVIS 

async def create_facture_from_devis(db: Session, devis_id: int, numero_facture: str | None = None, devis_data: dict | None = None) -> Facture:
    try:
        if devis_data:
            devis = devis_data
        else:
            devis = await get_devis_by_id(devis_id)

        if not isinstance(devis, dict):
            raise HTTPException(status_code=400, detail="Devis invalide reçu pour création de facture.")

        required_keys = {"client_id", "entreprise_id", "lignes"}
        missing_keys = required_keys - set(devis.keys())
        if missing_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Devis incomplet : clés manquantes {sorted(missing_keys)}"
            )

        lignes = []
        for index, l in enumerate(devis["lignes"], start=1):
            if not all(k in l for k in ("product_id", "quantite", "prix_unitaire")):
                raise HTTPException(
                    status_code=400,
                    detail=f"Ligne {index} du devis invalide : product_id, quantite et prix_unitaire sont requis"
                )
            lignes.append(LigneFactureCreate(
                product_id    = l["product_id"],
                quantite      = l["quantite"],
                prix_unitaire = l["prix_unitaire"],
            ))

        entreprise_id = devis.get("entreprise_id") or 1

        data = FactureCreate(
            numero_facture = numero_facture,
            client_id      = devis["client_id"],
            entreprise_id  = entreprise_id,
            source         = "DEVIS",
            source_id      = devis_id,
            lignes         = lignes,
        )

        return await create_facture(db, data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Champ manquant dans le devis : {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne facture : {str(e)}")


async def create_facture_groupee_from_bls(db: Session, payload: dict) -> Facture:
    """
    Crée une facture groupée depuis plusieurs BL.
    Les numéros BL doivent être fournis dans `description` de chaque ligne.
    """
    try:
        lignes = []
        for index, l in enumerate(payload.get("lignes", []), start=1):
            if not all(k in l for k in ("product_id", "quantite", "prix_unitaire")):
                raise HTTPException(
                    status_code=400,
                    detail=f"Ligne {index} invalide : product_id, quantite et prix_unitaire sont requis"
                )
            lignes.append(LigneFactureCreate(
                product_id=l["product_id"],
                description=l.get("description"),
                quantite=l["quantite"],
                prix_unitaire=l["prix_unitaire"],
            ))

        data = FactureCreate(
            numero_facture=payload.get("numero_facture"),
            client_id=payload["client_id"],
            entreprise_id=payload.get("entreprise_id", 1),
            source=payload.get("source", "BL_GROUPE"),
            source_id=payload.get("source_id"),
            lignes=lignes,
        )
        return await create_facture(db, data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Champ manquant dans la facture groupée : {e}")
