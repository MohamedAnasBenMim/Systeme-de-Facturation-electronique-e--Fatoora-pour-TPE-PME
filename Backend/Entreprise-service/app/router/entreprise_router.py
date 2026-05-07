# app/router/entreprise_router.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.entreprise_service import EntrepriseService
from app.repositories.entreprise_repository import EntrepriseRepository
from app.schemas.entreprise_schema import (
    EntrepriseCreate, EntrepriseUpdate,
    EntrepriseResponse, EntrepriseConfigResponse, EntrepriseDetailResponse
)
from app.core.dependencies import get_current_user
from app.models.entreprise import Entreprise

router = APIRouter(prefix="/entreprises", tags=["Entreprise"])


# ─── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=EntrepriseResponse, status_code=201)
def create(
    payload: EntrepriseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Crée le profil entreprise de l'utilisateur connecté."""
    return EntrepriseService(db).create(payload, owner_id=current_user["user_id"])
    
@router.get("/by-owner/{owner_id}")
def get_by_owner(owner_id: int, db: Session = Depends(get_db)):
    entreprise = db.query(Entreprise).filter(
        Entreprise.owner_id == owner_id
    ).first()
    if not entreprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    return {"id": entreprise.id, "nom": entreprise.nom}

# ─── GET MON PROFIL (simple) ───────────────────────────────────────────────────
@router.get("/mon-profil", response_model=EntrepriseResponse)
def get_mon_profil(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retourne le profil entreprise de l'utilisateur connecté."""
    return EntrepriseService(db).get_mon_profil(owner_id=current_user["user_id"])


# ─── GET MON PROFIL (complet) ─────────────────────────────────────────────────
@router.get("/mon-profil/complet", response_model=EntrepriseDetailResponse)
def get_profil_complet(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retourne le profil complet avec membres et comptes bancaires."""
    e = EntrepriseRepository(db).find_by_owner_id(current_user["user_id"])
    if not e:
        raise HTTPException(status_code=404, detail="Profil introuvable")
    return EntrepriseDetailResponse.model_validate(e)


# ─── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/mon-profil", response_model=EntrepriseResponse)
def update(
    payload: EntrepriseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Met à jour le profil entreprise de l'utilisateur connecté."""
    return EntrepriseService(db).update(payload, owner_id=current_user["user_id"])


# ─── UPLOAD LOGO ───────────────────────────────────────────────────────────────
@router.post("/mon-profil/logo/{filename}", response_model=EntrepriseResponse)
def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Upload le logo de l'entreprise (JPG, PNG ou WebP)."""
    return EntrepriseService(db).upload_logo(file, owner_id=current_user["user_id"])


# ─── GET BY ID (inter-services, sans auth) ────────────────────────────────────
@router.get("/{entreprise_id}", response_model=EntrepriseResponse)
def get_by_id(
    entreprise_id: int,
    db: Session = Depends(get_db),
):
    """Retourne une entreprise par son ID — accessible sans authentification (inter-services)."""
    return EntrepriseService(db).get_by_id(entreprise_id)


# ─── GET CONFIG (inter-services, sans auth) ───────────────────────────────────
@router.get("/{entreprise_id}/config", response_model=EntrepriseConfigResponse)
def get_config(
    entreprise_id: int,
    db: Session = Depends(get_db),
):
    """Retourne la configuration d'une entreprise — accessible sans authentification (inter-services)."""
    return EntrepriseService(db).get_config(entreprise_id)