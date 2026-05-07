# app/router/internal.py
"""
Routes internes appelées uniquement par d'autres microservices
(ms-auth lors du register, ms-facture pour générer un PDF, etc.)
Protégées par un secret interne, PAS par le JWT utilisateur.
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.entreprise import Entreprise
from app.repositories.entreprise_repository import EntrepriseRepository
from app.schemas.entreprise_schema import EntrepriseResponse, EntrepriseConfigResponse
from app.core.config import settings

router = APIRouter(prefix="/internal", tags=["Internal"])


def _verify_internal_secret(x_internal_secret: str = Header(...)):
    """Vérifie que la requête vient bien d'un microservice interne."""
    if x_internal_secret != settings.INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Accès interdit")


# ─── INIT (appelé par ms-auth à l'inscription) ────────────────────────────────
@router.post("/init", dependencies=[Depends(_verify_internal_secret)])
def init(
    data: dict,
    db: Session = Depends(get_db),
):
    """
    Initialise un profil entreprise vide lors de l'inscription d'un utilisateur.
    Appelé uniquement par ms-auth.
    """
    owner_id = data.get("user_id")
    if not owner_id:
        raise HTTPException(status_code=400, detail="user_id manquant")

    # Vérifie si un profil existe déjà
    existing = EntrepriseRepository(db).find_by_owner_id(owner_id)
    if existing:
        return {"ok": True, "entreprise_id": existing.id, "created": False}

    e = Entreprise(
        owner_id = owner_id,
        nom      = data.get("nom", "Mon Entreprise"),
        email    = data.get("email", ""),
        adresse  = data.get("adresse", "À compléter"),
        ville    = data.get("ville", "À compléter"),
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return {"ok": True, "entreprise_id": e.id, "created": True}


# ─── PROFIL (appelé par ms-facture pour générer le PDF) ──────────────────────
@router.get("/profil/{entreprise_id}",
            response_model=EntrepriseConfigResponse,
            dependencies=[Depends(_verify_internal_secret)])
def profil_interne(
    entreprise_id: int,
    db: Session = Depends(get_db),
):
    """
    Retourne la config complète d'une entreprise pour la génération de documents.
    Appelé uniquement par ms-facture, ms-devis, etc.
    """
    e = EntrepriseRepository(db).find_by_id(entreprise_id)
    if not e:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    return EntrepriseConfigResponse.model_validate(e)