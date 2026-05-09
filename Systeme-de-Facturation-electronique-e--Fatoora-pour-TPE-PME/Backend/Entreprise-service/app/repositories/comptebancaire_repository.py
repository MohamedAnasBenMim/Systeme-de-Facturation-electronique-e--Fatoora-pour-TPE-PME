# app/repositories/comptebancaire_repository.py
from sqlalchemy.orm import Session
from app.models.compteBancaire import CompteBancaire


class CompteBancaireRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_all(self, entreprise_id: int) -> list[CompteBancaire]:
        """Retourne uniquement les comptes de l'entreprise concernée."""
        return self.db.query(CompteBancaire)\
            .filter(CompteBancaire.entreprise_id == entreprise_id)\
            .all()

    def find_by_id(self, compte_id: int, entreprise_id: int) -> CompteBancaire | None:
        """Trouve un compte en vérifiant qu'il appartient bien à l'entreprise."""
        return self.db.query(CompteBancaire)\
            .filter(
                CompteBancaire.id == compte_id,
                CompteBancaire.entreprise_id == entreprise_id
            ).first()

    def save(self, data: dict) -> CompteBancaire:
        compte = CompteBancaire(**data)
        self.db.add(compte)
        self.db.commit()
        self.db.refresh(compte)
        return compte

    def update(self, compte: CompteBancaire, data: dict) -> CompteBancaire:
        for key, value in data.items():
            setattr(compte, key, value)
        self.db.commit()
        self.db.refresh(compte)
        return compte

    def delete(self, compte: CompteBancaire) -> None:
        self.db.delete(compte)
        self.db.commit()