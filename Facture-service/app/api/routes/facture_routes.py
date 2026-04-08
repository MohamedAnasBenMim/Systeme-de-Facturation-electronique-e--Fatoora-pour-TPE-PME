from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.facture_schema import FactureCreate, FactureResponse
from app.schemas.ligne_facture_schema import LigneFactureCreate
from app.services import facture_service
from typing import List
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/factures", tags=["Factures"], dependencies=[Depends(get_current_user)])


@router.post("/")
def create_facture_route(client: str, lignes: List[LigneFactureCreate], db: Session = Depends(get_db)):
    return facture_service.create_facture(db, client, lignes)

# 🔹 GET ALL
@router.get("/")
def get_all_factures_route(db: Session = Depends(get_db)):
    return facture_service.get_all_factures(db)

# 🔹 GET ONE
@router.get("/{facture_id}")
def get_facture_route(facture_id: int, db: Session = Depends(get_db)):
    return facture_service.get_facture(db, facture_id)

# 🔹 UPDATE
@router.put("/{facture_id}")
def update_facture_route(facture_id: int, client: str = None, lignes: List[LigneFactureCreate] = None, db: Session = Depends(get_db)):
    return facture_service.update_facture(db, facture_id, client, lignes)

# 🔹 DELETE
@router.delete("/{facture_id}")
def delete_facture_route(facture_id: int, db: Session = Depends(get_db)):
    return facture_service.delete_facture(db, facture_id)

