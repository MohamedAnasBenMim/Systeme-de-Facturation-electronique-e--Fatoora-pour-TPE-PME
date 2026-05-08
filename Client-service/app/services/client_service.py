from sqlalchemy.orm import Session
from app.repositories.client_repository import ClientRepository
from app.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse



class ClientService:

    def __init__(self, db: Session):
        self.repo = ClientRepository(db)

    def create_client(self, data: ClientCreate) -> ClientResponse:
        if self.repo.get_by_email(data.email):
            raise EmailAlreadyExistsException(data.email)

        if data.matricule_fiscal and self.repo.get_by_matricule_fiscal(data.matricule_fiscal):
            raise MatriculeFiscalExistsException(data.matricule_fiscal)

        client = self.repo.create(data)
        return ClientResponse.model_validate(client)

    def get_client(self, client_id: int) -> ClientResponse:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundException(client_id)
        return ClientResponse.model_validate(client)

    def get_all_clients(self, skip: int = 0, limit: int = 100) -> ClientListResponse:
        clients = self.repo.get_all(skip=skip, limit=limit)
        total = self.repo.count()
        return ClientListResponse(
            total=total,
            clients=[ClientResponse.model_validate(c) for c in clients],
        )

    def update_client(self, client_id: int, data: ClientUpdate) -> ClientResponse:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundException(client_id)

        existing = self.repo.get_by_email(data.email)
        if existing and existing.id != client_id:
            raise EmailAlreadyExistsException(data.email)

        updated = self.repo.update(client, data)
        return ClientResponse.model_validate(updated)

    def delete_client(self, client_id: int) -> None:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundException(client_id)
        self.repo.delete(client)

    def get_client_by_email(self, email: str) -> ClientResponse:
        client = self.repo.get_by_email(email)
        if not client:
            raise ClientNotFoundException(0)
        return ClientResponse.model_validate(client)