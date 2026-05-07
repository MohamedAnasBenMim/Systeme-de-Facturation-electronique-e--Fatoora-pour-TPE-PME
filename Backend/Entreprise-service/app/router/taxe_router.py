# ms-entreprise/app/router/taxe_router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.taxe_service import TaxeService
from app.schemas.taxe import (
    TaxeCreate, TaxeUpdate, TaxeResponse,
    GroupeTaxeCreate, GroupeTaxeUpdate, GroupeTaxeResponse,
)
from app.core.dependencies import get_current_entreprise_id
from typing import List

router = APIRouter(prefix="/taxes", tags=["Taxes"])

def get_service(db: Session = Depends(get_db)):
    return TaxeService(db)

# ══════════════════════════════════════════════
# ✅ GROUPES EN PREMIER (routes statiques)
# ══════════════════════════════════════════════

@router.get("/groupes", response_model=List[GroupeTaxeResponse])
def list_groupes(
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: TaxeService = Depends(get_service),
):
    return service.list_groupes(entreprise_id)

@router.post("/groupes", response_model=GroupeTaxeResponse, status_code=status.HTTP_201_CREATED)
def create_groupe(
    data: GroupeTaxeCreate,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: TaxeService = Depends(get_service),
):
    return service.create_groupe(entreprise_id, data)

@router.patch("/groupes/{groupe_id}", response_model=GroupeTaxeResponse)
def update_groupe(
    groupe_id: str,
    data: GroupeTaxeUpdate,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: TaxeService = Depends(get_service),
):
    return service.update_groupe(entreprise_id, groupe_id, data)

@router.delete("/groupes/{groupe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_groupe(
    groupe_id: str,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: TaxeService = Depends(get_service),
):
    service.delete_groupe(entreprise_id, groupe_id)

#  TAXES SIMPLES EN DERNIER (routes dynamiques)

@router.get("", response_model=List[TaxeResponse])
def list_taxes(
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: TaxeService = Depends(get_service),
):
    return service.list_taxes(entreprise_id)

@router.post("", response_model=TaxeResponse, status_code=status.HTTP_201_CREATED)
def create_taxe(
    data: TaxeCreate,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: TaxeService = Depends(get_service),
):
    return service.create_taxe(entreprise_id, data)

@router.patch("/{taxe_id}", response_model=TaxeResponse)
def update_taxe(
    taxe_id: str,
    data: TaxeUpdate,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: TaxeService = Depends(get_service),
):
    return service.update_taxe(entreprise_id, taxe_id, data)

@router.delete("/{taxe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_taxe(
    taxe_id: str,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: TaxeService = Depends(get_service),
):
    service.delete_taxe(entreprise_id, taxe_id)