from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.devis_schema import DevisCreate, DevisResponse
from app.services.devis_service import DevisService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/devis", tags=["Devis"], dependencies=[Depends(get_current_user)])

@router.post("/", response_model=DevisResponse)
def create_devis_route(devis: DevisCreate, db: Session = Depends(get_db)):
    service = DevisService(db)
    db_devis = service.create(devis)
    return db_devis

@router.get("/{devis_id}", response_model=DevisResponse)
def get_devis_route(devis_id: int, db: Session = Depends(get_db)):
    service = DevisService(db)
    db_devis = service.get_one(devis_id)
    if not db_devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    return db_devis

@router.get("/", response_model=list[DevisResponse])
def get_all_devis_route(db: Session = Depends(get_db)):
    service = DevisService(db)
    return service.get_all()

@router.delete("/{devis_id}", response_model=DevisResponse)
def delete_devis_route(devis_id: int, db: Session = Depends(get_db)):
    service = DevisService(db)
    db_devis = service.delete(devis_id)
    if not db_devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    return db_devis