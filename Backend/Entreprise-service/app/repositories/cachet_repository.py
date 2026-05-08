from sqlalchemy.orm import Session
from app.models.cachet import Cachet
import uuid

class CachetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_entreprise(self, entreprise_id: int) -> Cachet | None:
        return self.db.query(Cachet).filter(
            Cachet.entreprise_id == entreprise_id
        ).first()

    def upsert(self, entreprise_id: int, image_data: bytes, image_mime: str, nom: str | None) -> Cachet:
        cachet = self.get_by_entreprise(entreprise_id)
        if cachet:
            # mise à jour
            cachet.image_data = image_data
            cachet.image_mime = image_mime
            cachet.nom        = nom
        else:
            # création
            cachet = Cachet(
                id            = uuid.uuid4(),
                entreprise_id = entreprise_id,
                image_data    = image_data,
                image_mime    = image_mime,
                nom           = nom,
            )
            self.db.add(cachet)
        self.db.commit()
        self.db.refresh(cachet)
        return cachet

    def delete(self, entreprise_id: int) -> bool:
        cachet = self.get_by_entreprise(entreprise_id)
        if not cachet:
            return False
        self.db.delete(cachet)
        self.db.commit()
        return True