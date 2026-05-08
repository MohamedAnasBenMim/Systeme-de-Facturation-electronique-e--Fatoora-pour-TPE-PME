from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from app.services.client_service import ClientService
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
    dependencies=[Depends(get_current_user)]
)


def get_service(db: Session = Depends(get_db)) -> ClientService:
    return ClientService(db)


@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau client",
)
def create_client(
    data: ClientCreate,
    service: ClientService = Depends(get_service),
):
    return service.create_client(data)


@router.get(
    "/",
    response_model=ClientListResponse,
    summary="Lister tous les clients",
)
def list_clients(
    skip: int = 0,
    limit: int = 100,
    service: ClientService = Depends(get_service),
):
    return service.get_all_clients(skip=skip, limit=limit)


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Obtenir un client par ID",
)
def get_client(
    client_id: int,
    service: ClientService = Depends(get_service),
):
    return service.get_client(client_id)


@router.get(
    "/email/{email}",
    response_model=ClientResponse,
    summary="Obtenir un client par email",
)
def get_client_by_email(
    email: str,
    service: ClientService = Depends(get_service),
):
    return service.get_client_by_email(email)


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Mettre à jour un client",
)
def update_client(
    client_id: int,
    data: ClientUpdate,
    service: ClientService = Depends(get_service),
):
    return service.update_client(client_id, data)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un client",
)
def delete_client(
    client_id: int,
    service: ClientService = Depends(get_service),
):
    service.delete_client(client_id)