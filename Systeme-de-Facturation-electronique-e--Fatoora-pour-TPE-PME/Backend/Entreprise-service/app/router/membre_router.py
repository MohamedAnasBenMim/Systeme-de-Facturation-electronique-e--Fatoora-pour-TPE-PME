# app/router/membre_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.membre_service import MembreService
from app.schemas.membre_schema import MembreCreate, MembreUpdate, MembreResponse
from app.core.dependencies import get_current_user
from app.repositories.entreprise_repository import EntrepriseRepository

router = APIRouter(
    prefix="/membres",
    tags=["Membres"],
    dependencies=[Depends(get_current_user)]
)


def _get_entreprise_id(current_user: dict, db: Session) -> int:
    """Récupère l'entreprise_id à partir de l'utilisateur connecté (owner_id)."""
    e = EntrepriseRepository(db).find_by_owner_id(current_user["user_id"])
    if not e:
        raise HTTPException(
            status_code=404,
            detail="Profil entreprise introuvable — créez votre profil d'abord"
        )
    return e.id


@router.get("/", response_model=list[MembreResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retourne tous les membres de l'entreprise connectée."""
    entreprise_id = _get_entreprise_id(current_user, db)
    return MembreService(db).get_all(entreprise_id)


@router.post("/inviter", response_model=MembreResponse, status_code=201)
async def inviter(
    payload: MembreCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Invite un nouveau membre dans l'entreprise."""
    entreprise_id = _get_entreprise_id(current_user, db)
    return await MembreService(db).inviter(payload, entreprise_id)


@router.put("/{membre_id}", response_model=MembreResponse)
def update(
    membre_id: int,
    payload: MembreUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Met à jour le rôle, statut ou permissions d'un membre."""
    entreprise_id = _get_entreprise_id(current_user, db)
    return MembreService(db).update(membre_id, payload, entreprise_id)


@router.delete("/{membre_id}", status_code=204)
def supprimer(
    membre_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Supprime un membre de l'entreprise."""
    entreprise_id = _get_entreprise_id(current_user, db)
    MembreService(db).supprimer(membre_id, entreprise_id)