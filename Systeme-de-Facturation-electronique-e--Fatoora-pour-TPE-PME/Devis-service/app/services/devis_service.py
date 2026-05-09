from sqlalchemy.orm import Session
from app.repositories.devis_repository import create_devis, get_devis, get_all_devis, delete_devis
from app.schemas.devis_schema import DevisCreate

class DevisService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, devis: DevisCreate):
        return create_devis(self.db, devis)

    def get_one(self, devis_id: int):
        return get_devis(self.db, devis_id)

    def get_all(self):
        return get_all_devis(self.db)

    def delete(self, devis_id: int):
        return delete_devis(self.db, devis_id)