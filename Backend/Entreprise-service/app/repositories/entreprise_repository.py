from sqlalchemy.orm import Session
from app.models.entreprise import Entreprise


class EntrepriseRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_owner_id(self, owner_id: int) -> Entreprise | None:
        return self.db.query(Entreprise)\
            .filter(Entreprise.owner_id == owner_id)\
            .first()

    def find_by_id(self, entreprise_id: int) -> Entreprise | None:
        return self.db.query(Entreprise)\
            .filter(Entreprise.id == entreprise_id)\
            .first()

    def save(self, data: dict) -> Entreprise:
        entreprise = Entreprise(**data)
        self.db.add(entreprise)
        self.db.commit()
        self.db.refresh(entreprise)
        return entreprise

    def update(self, entreprise: Entreprise, data: dict) -> Entreprise:
        for key, value in data.items():
            setattr(entreprise, key, value)
        self.db.commit()
        self.db.refresh(entreprise)
        return entreprise

    def update_logo(self, entreprise: Entreprise, logo_url: str) -> Entreprise:
        entreprise.logo_url = logo_url
        self.db.commit()
        self.db.refresh(entreprise)
        return entreprise