from sqlalchemy.orm import Session
from app.models.facture import Facture


class NumerotationService:

    def __init__(self, db: Session):
        self.db = db

    def generer_numero_facture(self) -> str:
        from datetime import date
        annee = date.today().year

        from sqlalchemy import extract
        count = (
            self.db.query(Facture)
            .filter(extract("year", Facture.date_creation) == annee)
            .count()
        )
        numero = count + 1
        return f"FAC-{annee}-{str(numero).zfill(5)}"