# app/router/comptebancaire_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.comptebancaire_service import CompteBancaireService
from app.schemas.comptebancaire_schema import (
    CompteBancaireCreate, CompteBancaireUpdate, CompteBancaireResponse
)
from app.core.dependencies import get_current_user
from app.repositories.entreprise_repository import EntrepriseRepository
from fastapi import HTTPException

router = APIRouter(
    prefix="/comptes-bancaires",
    tags=["Comptes Bancaires"],
    dependencies=[Depends(get_current_user)]
)


def _get_entreprise_id(current_user: dict, db: Session) -> int:
    """Récupère l'entreprise_id de l'utilisateur connecté."""
    e = EntrepriseRepository(db).find_by_owner_id(current_user["user_id"])
    if not e:
        raise HTTPException(
            status_code=404,
            detail="Profil entreprise introuvable — créez votre profil d'abord"
        )
    return e.id


@router.get("/", response_model=list[CompteBancaireResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retourne tous les comptes bancaires de l'entreprise connectée."""
    entreprise_id = _get_entreprise_id(current_user, db)
    return CompteBancaireService(db).get_all(entreprise_id)


@router.post("/", response_model=CompteBancaireResponse, status_code=201)
def create(
    payload: CompteBancaireCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Crée un compte bancaire pour l'entreprise connectée."""
    entreprise_id = _get_entreprise_id(current_user, db)
    return CompteBancaireService(db).create(payload, entreprise_id)


@router.put("/{compte_id}", response_model=CompteBancaireResponse)
def update(
    compte_id: int,
    payload: CompteBancaireUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Met à jour un compte bancaire."""
    entreprise_id = _get_entreprise_id(current_user, db)
    return CompteBancaireService(db).update(compte_id, payload, entreprise_id)


@router.delete("/{compte_id}", status_code=204)
def delete(
    compte_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Supprime un compte bancaire."""
    entreprise_id = _get_entreprise_id(current_user, db)
    CompteBancaireService(db).delete(compte_id, entreprise_id)