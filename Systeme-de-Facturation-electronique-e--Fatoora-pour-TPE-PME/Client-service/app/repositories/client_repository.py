from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate
from typing import Optional


class ClientRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_by_email(self, email: str) -> Optional[Client]:
        return self.db.query(Client).filter(Client.email == email).first()

    def get_by_matricule_fiscal(self, matricule: str) -> Optional[Client]:
        return self.db.query(Client).filter(
            Client.matricule_fiscal == matricule
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Client]:
        return self.db.query(Client).offset(skip).limit(limit).all()

    def count(self) -> int:
        return self.db.query(Client).count()

    def create(self, data: ClientCreate) -> Client:
        client = Client(
            nom=data.nom,
            prenom=data.prenom,
            email=data.email,
            telephone=data.telephone,
            adresse=data.adresse,
            matricule_fiscal=data.matricule_fiscal,
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def update(self, client: Client, data: ClientUpdate) -> Client:
        client.nom = data.nom
        client.prenom = data.prenom
        client.email = data.email
        client.telephone = data.telephone
        client.adresse = data.adresse
        client.matricule_fiscal = data.matricule_fiscal
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete(self, client: Client) -> None:
        self.db.delete(client)
        self.db.commit()