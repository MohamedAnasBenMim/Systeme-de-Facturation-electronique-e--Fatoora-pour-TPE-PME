
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date

from app.db.database import get_db
from app.schemas.achat_schema import (
    FournisseurCreate, FournisseurUpdate, FournisseurResponse,
    BonCommandeCreate, BonCommandeResponse, BonCommandeConfirm,
    ReceptionCreate, ReceptionResponse,
    BonRetourCreate, BonRetourResponse,
    FactureFournisseurCreate, FactureFournisseurResponse,
    LitigeFactureResponse,
    StatistiquesAchatsResponse
)
from app.services import achat_service
from app.models.achat import (
    BonCommande, Reception, BonRetour, FactureFournisseur, LitigeFacture,
    StatutFactureFournisseur, Fournisseur
)


router = APIRouter(
    prefix="/achats"
    
)


# FOURNISSEURS

@router.post("/fournisseurs", response_model=FournisseurResponse)
def create_fournisseur(
    data: FournisseurCreate,
    db: Session = Depends(get_db)
):
    """Crée un nouveau fournisseur."""
    return achat_service.create_fournisseur(db, data)


@router.get("/fournisseurs", response_model=list[FournisseurResponse])
def list_fournisseurs(
    actifs_seulement: bool = True,
    db: Session = Depends(get_db)
):
    """Liste tous les fournisseurs."""
    return achat_service.get_all_fournisseurs(db, actifs_seulement)


@router.get("/fournisseurs/{fournisseur_id}", response_model=FournisseurResponse)
def get_fournisseur(
    fournisseur_id: int,
    db: Session = Depends(get_db)
):
    """Récupère un fournisseur par ID."""
    return achat_service.get_fournisseur_by_id(db, fournisseur_id)


@router.put("/fournisseurs/{fournisseur_id}", response_model=FournisseurResponse)
def update_fournisseur(
    fournisseur_id: int,
    data: FournisseurUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un fournisseur."""
    return achat_service.update_fournisseur(db, fournisseur_id, data)


# ============ BONS DE COMMANDE ============

@router.post("/bons-commande", response_model=BonCommandeResponse)
async def create_bc(
    data: BonCommandeCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """Crée un nouveau bon de commande (statut: BROUILLON)."""
    return await achat_service.create_bon_commande(db, data, user_id)


@router.get("/bons-commande", response_model=list[BonCommandeResponse])
def list_bcs(
    entreprise_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Liste tous les bons de commande."""
    return achat_service.get_all_bons_commande(db, entreprise_id)


@router.get("/bons-commande/{bc_id}", response_model=BonCommandeResponse)
def get_bc(
    bc_id: int,
    db: Session = Depends(get_db)
):
    """Récupère un bon de commande par ID."""
    return achat_service.get_bon_commande(db, bc_id)


@router.post("/bons-commande/{bc_id}/confirmer", response_model=BonCommandeResponse)
def confirm_bc(
    bc_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """
    Confirme un bon de commande.
    Une fois confirmé, le BC devient IMMUABLE et prêt pour réception.
    """
    return achat_service.confirm_bon_commande(db, bc_id, user_id)


# ============ RÉCEPTIONS ============

@router.post("/receptions", response_model=ReceptionResponse)
async def create_reception(
    data: ReceptionCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """
    Crée une nouvelle réception.
    Effectue un contrôle strict: jamais plus que commandé!
    """
    return await achat_service.create_reception(db, data, user_id)


@router.get("/receptions/{reception_id}", response_model=ReceptionResponse)
def get_reception(
    reception_id: int,
    db: Session = Depends(get_db)
):
    """Récupère une réception par ID."""
    return achat_service.get_reception(db, reception_id)


# ============ BONS DE RETOUR ============

@router.post("/bons-retour", response_model=BonRetourResponse)
async def create_bon_retour(
    data: BonRetourCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """Crée un bon de retour pour articles non conformes."""
    return await achat_service.create_bon_retour(db, data, user_id)


@router.post("/bons-retour/{br_id}/valider")
def validate_bon_retour(
    br_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """
    Valide un bon de retour et génère automatiquement un avoir fournisseur.
    """
    avoir = achat_service.validate_bon_retour(db, br_id, user_id)
    return {"status": "success", "avoir_id": avoir.id, "numero_avoir": avoir.numero_avoir}


# ============ FACTURES FOURNISSEUR ============

@router.post("/factures-fournisseur", response_model=FactureFournisseurResponse)
async def create_facture_fournisseur(
    data: FactureFournisseurCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """
    Crée une facture fournisseur.
    Effectue automatiquement le rapprochement 3 voies (BC vs Réception vs Facture).
    Bloque la facture en EN_LITIGE si des écarts > seuil sont détectés.
    """
    return await achat_service.create_facture_fournisseur(db, data, user_id)


@router.get("/factures-fournisseur", response_model=list[FactureFournisseurResponse])
def list_factures_fournisseur(
    entreprise_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Liste toutes les factures fournisseur."""
    return achat_service.get_all_factures_fournisseur(db, entreprise_id)


@router.get("/factures-fournisseur/{facture_id}", response_model=FactureFournisseurResponse)
def get_facture_fournisseur(
    facture_id: int,
    db: Session = Depends(get_db)
):
    """Récupère une facture fournisseur par ID."""
    return achat_service.get_facture_fournisseur(db, facture_id)


# ============ LITIGES ============

@router.get("/litiges", response_model=list[LitigeFactureResponse])
def list_litiges(
    entreprise_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Liste tous les litiges (factures avec écarts non résolus)."""
    q = db.query(LitigeFacture).filter(LitigeFacture.resolu == False)
    if entreprise_id:
        q = q.join(FactureFournisseur).filter(FactureFournisseur.entreprise_id == entreprise_id)
    return q.all()


@router.get("/litiges/{facture_id}", response_model=LitigeFactureResponse)
def get_litige(
    facture_id: int,
    db: Session = Depends(get_db)
):
    """Récupère le litige associé à une facture."""
    litige = db.query(LitigeFacture).filter(LitigeFacture.facture_id == facture_id).first()
    if not litige:
        raise HTTPException(status_code=404, detail="Aucun litige pour cette facture")
    return litige


@router.post("/litiges/{facture_id}/resoudre")
def resolve_litige(
    facture_id: int,
    resolution: str,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
):
    """Résout un litige."""
    from datetime import datetime
    
    litige = db.query(LitigeFacture).filter(LitigeFacture.facture_id == facture_id).first()
    if not litige:
        raise HTTPException(status_code=404, detail="Aucun litige pour cette facture")
    
    litige.resolu = True
    litige.resolution = resolution
    litige.date_resolution = datetime.utcnow()
    litige.resolu_par_user_id = user_id
    
    facture = db.query(FactureFournisseur).filter(FactureFournisseur.id == facture_id).first()
    facture.statut = StatutFactureFournisseur.VALIDEE
    
    db.commit()
    return {"status": "success", "message": "Litige résolu"}


# ============ STATISTIQUES ============

@router.get("/stats/global", response_model=StatistiquesAchatsResponse)
def stats_achats_global(
    entreprise_id: int,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Statistiques globales d'achats pour une entreprise."""
    q = db.query(BonCommande).filter(BonCommande.entreprise_id == entreprise_id)
    if date_debut:
        q = q.filter(BonCommande.date_creation >= date_debut)
    if date_fin:
        q = q.filter(BonCommande.date_creation <= date_fin)
    
    bcs = q.all()
    
    # Calculs
    total_depenses = sum(bc.total_ttc for bc in bcs if bc.statut.value in ["LIVREE", "DIFFERENCIEE"])
    nombre_litiges = db.query(LitigeFacture).filter(LitigeFacture.resolu == False).count()
    
    return {
        "total_depenses": round(total_depenses, 3),
        "total_depenses_payees": 0.0,  # À calculer depuis le microservice paiement
        "nombre_bons_commande": len(bcs),
        "nombre_factures_en_litige": nombre_litiges,
        "periode": f"{date_debut} à {date_fin}" if date_debut and date_fin else "Tous les temps"
    }


@router.get("/stats/fournisseurs-fideles")
def stats_fournisseurs_fideles(
    entreprise_id: int,
    limite: int = 5,
    db: Session = Depends(get_db)
):
    """Top fournisseurs par dépenses totales."""
    resultats = (
        db.query(
            BonCommande.fournisseur_id,
            func.count(BonCommande.id).label("nb_bcs"),
            func.sum(BonCommande.total_ttc).label("depenses_total")
        )
        .filter(BonCommande.entreprise_id == entreprise_id)
        .group_by(BonCommande.fournisseur_id)
        .order_by(func.sum(BonCommande.total_ttc).desc())
        .limit(limite)
        .all()
    )
    
    return [
        {
            "fournisseur_id": r.fournisseur_id,
            "nb_bcs": r.nb_bcs,
            "depenses_total": round(r.depenses_total, 3),
        }
        for r in resultats
    ]


# ============ AUDIT TRAIL ============

@router.get("/audit-trail/bon-commande/{bc_id}")
def get_audit_trail_bc(
    bc_id: int,
    db: Session = Depends(get_db)
):
    """Récupère l'historique complet d'un bon de commande."""
    from app.models.achat import AuditTrail
    
    trail = db.query(AuditTrail).filter(AuditTrail.bon_commande_id == bc_id).all()
    return [
        {
            "action": t.action,
            "ancien_statut": t.ancien_statut,
            "nouveau_statut": t.nouveau_statut,
            "user_id": t.user_id,
            "date_action": t.date_action,
            "details": t.details_modification
        }
        for t in trail
    ]


@router.get("/audit-trail/facture/{facture_id}")
def get_audit_trail_facture(
    facture_id: int,
    db: Session = Depends(get_db)
):
    """Récupère l'historique complet d'une facture."""
    from app.models.achat import AuditTrail
    
    trail = db.query(AuditTrail).filter(AuditTrail.facture_fournisseur_id == facture_id).all()
    return [
        {
            "action": t.action,
            "ancien_statut": t.ancien_statut,
            "nouveau_statut": t.nouveau_statut,
            "user_id": t.user_id,
            "date_action": t.date_action,
            "details": t.details_modification
        }
        for t in trail
    ]