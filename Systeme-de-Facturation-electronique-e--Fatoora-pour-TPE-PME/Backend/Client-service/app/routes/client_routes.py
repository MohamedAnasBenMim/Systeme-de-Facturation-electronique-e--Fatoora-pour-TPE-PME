from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
    PotentialDuplicateResponse,
)
from app.services.client_service import ClientService


router = APIRouter(prefix="/clients", tags=["Clients"])


def get_service(db: Session = Depends(get_db)) -> ClientService:
    return ClientService(db)


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, summary="Creer un nouveau client")
def create_client(data: ClientCreate, service: ClientService = Depends(get_service)):
    return service.create_client(data)


@router.get("/", response_model=ClientListResponse, summary="Lister les clients avec filtres")
def list_clients(
    skip: int = 0,
    limit: int = 100,
    nom: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    telephone: Optional[str] = Query(default=None),
    matricule_fiscal: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    type_client: Optional[Literal["PARTICULIER", "ENTREPRISE"]] = Query(default=None),
    secteur: Optional[str] = Query(default=None),
    niveau: Optional[Literal["STANDARD", "VIP"]] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    service: ClientService = Depends(get_service),
):
    return service.get_all_clients(
        skip=skip,
        limit=limit,
        nom=nom,
        email=email,
        telephone=telephone,
        matricule_fiscal=matricule_fiscal,
        is_active=is_active,
        type_client=type_client,
        secteur=secteur,
        niveau=niveau,
        tag=tag,
    )


@router.get("/{client_id}", response_model=ClientResponse, summary="Obtenir un client par ID")
def get_client(client_id: int, service: ClientService = Depends(get_service)):
    return service.get_client(client_id)


@router.get("/email/{email}", response_model=ClientResponse, summary="Obtenir un client par email")
def get_client_by_email(email: str, service: ClientService = Depends(get_service)):
    return service.get_client_by_email(email)


@router.get("/{client_id}/duplicates", response_model=list[PotentialDuplicateResponse], summary="Detecter des doublons potentiels")
def potential_duplicates(client_id: int, service: ClientService = Depends(get_service)):
    return service.potential_duplicates(client_id)


@router.put("/{client_id}", response_model=ClientResponse, summary="Mettre a jour un client")
def update_client(client_id: int, data: ClientUpdate, service: ClientService = Depends(get_service)):
    return service.update_client(client_id, data)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactiver un client")
def delete_client(client_id: int, service: ClientService = Depends(get_service)):
    service.delete_client(client_id)
