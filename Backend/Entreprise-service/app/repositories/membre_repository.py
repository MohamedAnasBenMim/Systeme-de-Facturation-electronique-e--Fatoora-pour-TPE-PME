from sqlalchemy.orm import Session
from app.models.membre import MembreEntreprise, StatutMembre
from datetime import datetime, timezone


class MembreRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_all(self, entreprise_id: int) -> list[MembreEntreprise]:
        return self.db.query(MembreEntreprise)\
            .filter(MembreEntreprise.entreprise_id == entreprise_id)\
            .all()

    def find_by_id(self, membre_id: int,
                   entreprise_id: int) -> MembreEntreprise | None:
        return self.db.query(MembreEntreprise)\
            .filter(
                MembreEntreprise.id == membre_id,
                MembreEntreprise.entreprise_id == entreprise_id
            ).first()

    def find_by_user_id(self, user_id: int) -> MembreEntreprise | None:
        return self.db.query(MembreEntreprise)\
            .filter(MembreEntreprise.user_id == user_id)\
            .first()

    def find_by_email(self, email: str,
                      entreprise_id: int) -> MembreEntreprise | None:
        return self.db.query(MembreEntreprise)\
            .filter(
                MembreEntreprise.email == email,
                MembreEntreprise.entreprise_id == entreprise_id
            ).first()

    def find_pending_by_email(self,
                               email: str) -> MembreEntreprise | None:
        """Cherche une invitation en attente par email"""
        return self.db.query(MembreEntreprise)\
            .filter(
                MembreEntreprise.email == email,
                MembreEntreprise.statut == StatutMembre.EN_ATTENTE
            ).first()

    def save(self, data: dict) -> MembreEntreprise:
        m = MembreEntreprise(**data)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return m

    def update(self, m: MembreEntreprise,
               data: dict) -> MembreEntreprise:
        for k, v in data.items():
            setattr(m, k, v)
        self.db.commit()
        self.db.refresh(m)
        return m

    def activer(self, m: MembreEntreprise,
                user_id: int) -> MembreEntreprise:
        m.user_id         = user_id
        m.statut          = StatutMembre.ACTIF
        m.date_acceptance = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(m)
        return m

    def delete(self, m: MembreEntreprise) -> None:
        self.db.delete(m)
        self.db.commit()