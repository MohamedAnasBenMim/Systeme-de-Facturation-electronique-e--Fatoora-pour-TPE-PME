import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.schemas.facture_schema import FactureCreate, FactureUpdate, FactureResponse
from app.services import facture_service
from typing import Optional
from datetime import date
from app.models.facture import Facture, StatutFacture
from app.models.ligneFacture import LigneFacture

router = APIRouter(
    prefix="/factures",
    tags=["Factures"]
)


def _token(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    return auth.replace("Bearer ", "") if auth.startswith("Bearer ") else None

# DASHBOARD

@router.get("/stats/global")
def stats_factures_global(
    entreprise_id: int,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Facture).filter(Facture.entreprise_id == entreprise_id)
    if date_debut:
        q = q.filter(Facture.date_creation >= date_debut)
    if date_fin:
        q = q.filter(Facture.date_creation <= date_fin)

    toutes = q.all()

    ca = sum(f.total_ttc for f in toutes if f.statut in [StatutFacture.VALIDEE, StatutFacture.PAYEE])
    revenus_encaisses = sum(f.total_ttc for f in toutes if f.statut == StatutFacture.PAYEE)
    creances = sum(f.total_ttc for f in toutes if f.statut == StatutFacture.VALIDEE)

    return {
        "chiffre_affaires":    round(ca, 3),
        "revenus_encaisses":   round(revenus_encaisses, 3),
        "creances_en_attente": round(creances, 3),
        "nombre_factures":     len(toutes),
    }


@router.get("/stats/clients-fideles")
def stats_clients_fideles(
    entreprise_id: int,
    limite: int = 5,
    db: Session = Depends(get_db)
):
    resultats = (
        db.query(
            Facture.client_id,
            func.count(Facture.id).label("nb_factures"),
            func.sum(Facture.total_ttc).label("ca_total")
        )
        .filter(
            Facture.entreprise_id == entreprise_id,
            Facture.statut.in_([StatutFacture.VALIDEE, StatutFacture.PAYEE])
        )
        .group_by(Facture.client_id)
        .order_by(func.sum(Facture.total_ttc).desc())
        .limit(limite)
        .all()
    )

    return [
        {
            "client_id":   r.client_id,
            "nb_factures": r.nb_factures,
            "ca_total":    round(r.ca_total, 3),
        }
        for r in resultats
    ]


@router.get("/stats/par-projet/{product_id}")
def stats_factures_par_projet(
    product_id: int,
    entreprise_id: int,
    db: Session = Depends(get_db)
):
    lignes = db.query(LigneFacture).join(Facture).filter(
        Facture.entreprise_id == entreprise_id,
        LigneFacture.product_id == product_id,
        Facture.statut.in_([StatutFacture.VALIDEE, StatutFacture.PAYEE])
    ).all()

    total_facture  = sum(l.montant_ligne for l in lignes)
    total_encaisse = sum(l.montant_ligne for l in lignes if l.facture.statut == StatutFacture.PAYEE)

    return {
        "product_id":     product_id,
        "total_facture":  round(total_facture, 3),
        "total_encaisse": round(total_encaisse, 3),
    }



# CRUD


@router.post("/", response_model=FactureResponse, status_code=201)
async def create_facture(
    data: FactureCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    return await facture_service.create_facture(db, data, token=_token(request))


class FactureFromDevisRequest(BaseModel):
    numero_facture: str | None = None
    devis_data: dict | None = None  # Full devis data instead of fetching it


class FactureGroupeeRequest(BaseModel):
    numero_facture: str | None = None
    client_id: int
    entreprise_id: int | None = 1
    source: str | None = "BL_GROUPE"
    source_id: int | None = None
    bl_ids: list[int] | None = None
    lignes: list[dict]


@router.post("/depuis-devis/{devis_id}", response_model=FactureResponse, status_code=201)
async def create_from_devis(
    devis_id: int,
    request: Request,
    data: FactureFromDevisRequest | None = None,
    db: Session = Depends(get_db)
):
    return await facture_service.create_facture_from_devis(
        db,
        devis_id,
        data.numero_facture if data else None,
        data.devis_data if data else None,
        token=_token(request),
    )


@router.post("/groupee", response_model=FactureResponse, status_code=201)
async def create_groupee_from_bls(
    data: FactureGroupeeRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    return await facture_service.create_facture_groupee_from_bls(db, data.model_dump(), token=_token(request))


@router.get("/", response_model=list[FactureResponse])
def get_all_factures(db: Session = Depends(get_db)):
    return facture_service.get_all_factures(db)


@router.get("/{facture_id}", response_model=FactureResponse)
def get_facture(facture_id: int, db: Session = Depends(get_db)):
    return facture_service.get_facture(db, facture_id)


@router.get("/{facture_id}/detail")
async def get_facture_detail(facture_id: int, db: Session = Depends(get_db)):
    return await facture_service.get_facture_detail(db, facture_id)


@router.put("/{facture_id}", response_model=FactureResponse)
async def update_facture(
    facture_id: int,
    data: FactureUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    return await facture_service.update_facture(db, facture_id, data, token=_token(request))


@router.delete("/{facture_id}")
def delete_facture(facture_id: int, db: Session = Depends(get_db)):
    return facture_service.delete_facture(db, facture_id)



# PDF


@router.get("/{facture_id}/pdf/download")
async def telecharger_pdf(facture_id: int, db: Session = Depends(get_db)):
    # Toujours régénérer pour garantir que le PDF reflète la dernière mise en forme
    # (ex: montant TTC en lettres ajouté automatiquement).
    pdf_path = await facture_service.generer_et_sauvegarder_pdf(db, facture_id)
    return FileResponse(path=pdf_path, media_type="application/pdf", filename=f"facture_{facture_id}.pdf")


@router.get("/{facture_id}/pdf/preview")
async def preview_pdf(facture_id: int, db: Session = Depends(get_db)):
    # Toujours régénérer pour garantir que le PDF reflète la dernière mise en forme
    # (ex: montant TTC en lettres ajouté automatiquement).
    pdf_path = await facture_service.generer_et_sauvegarder_pdf(db, facture_id)
    return FileResponse(path=pdf_path, media_type="application/pdf", headers={"Content-Disposition": "inline"}, filename=f"facture_{facture_id}.pdf")
