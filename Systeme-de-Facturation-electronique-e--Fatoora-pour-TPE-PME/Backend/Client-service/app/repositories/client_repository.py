from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate
from typing import Optional
from sqlalchemy import or_


class ClientRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_by_email(self, email: str) -> Optional[Client]:
        return self.db.query(Client).filter(Client.email == email).first()

    def get_by_telephone(self, telephone: str) -> Optional[Client]:
        return self.db.query(Client).filter(Client.telephone == telephone).first()

    def get_by_matricule_fiscal(self, matricule: str) -> Optional[Client]:
        return self.db.query(Client).filter(
            Client.matricule_fiscal == matricule
        ).first()

    def _base_query(self):
        return self.db.query(Client)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        nom: Optional[str] = None,
        email: Optional[str] = None,
        telephone: Optional[str] = None,
        matricule_fiscal: Optional[str] = None,
        is_active: Optional[bool] = None,
        type_client: Optional[str] = None,
        secteur: Optional[str] = None,
        niveau: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> list[Client]:
        q = self._base_query()
        if nom:
            pattern = f"%{nom.strip()}%"
            q = q.filter(or_(Client.nom.ilike(pattern), Client.prenom.ilike(pattern)))
        if email:
            q = q.filter(Client.email.ilike(f"%{email.strip()}%"))
        if telephone:
            q = q.filter(Client.telephone.ilike(f"%{telephone.strip()}%"))
        if matricule_fiscal:
            q = q.filter(Client.matricule_fiscal.ilike(f"%{matricule_fiscal.strip()}%"))
        if is_active is not None:
            q = q.filter(Client.is_active == is_active)
        if type_client:
            q = q.filter(Client.type_client == type_client)
        if secteur:
            q = q.filter(Client.secteur.ilike(f"%{secteur.strip()}%"))
        if niveau:
            q = q.filter(Client.niveau == niveau)
        if tag:
            q = q.filter(Client.tags.ilike(f"%{tag.strip().lower()}%"))
        return q.order_by(Client.id.desc()).offset(skip).limit(limit).all()

    def count(self, **filters) -> int:
        return len(self.get_all(skip=0, limit=10_000_000, **filters))

    def create(self, data: ClientCreate) -> Client:
        client = Client(
            nom=data.nom,
            prenom=data.prenom,
            email=data.email,
            telephone=data.telephone,
            adresse=data.adresse,
            matricule_fiscal=data.matricule_fiscal,
            type_client=data.type_client,
            secteur=data.secteur,
            tags=",".join(data.tags) if data.tags else None,
            niveau=data.niveau,
            is_active=data.is_active,
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
        client.type_client = data.type_client
        client.secteur = data.secteur
        client.tags = ",".join(data.tags) if data.tags else None
        client.niveau = data.niveau
        client.is_active = data.is_active
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete(self, client: Client) -> None:
        client.is_active = False
        self.db.commit()
