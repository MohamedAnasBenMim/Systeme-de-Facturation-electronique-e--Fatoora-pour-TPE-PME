from sqlalchemy.orm import Session
from typing import Optional
from app.models.BonCommande import BonCommande, StatutBonCommande
from app.models.ligne_commande import LigneBonCommande
from datetime import datetime, timezone

class BonCommandeRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_all(self, page: int = 1, page_size: int = 10):
        query = self.db.query(BonCommande).order_by(BonCommande.date_creation.desc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    def find_by_id(self, bc_id: int) -> Optional[BonCommande]:
        return self.db.query(BonCommande).filter(BonCommande.id == bc_id).first()

    def find_by_devis(self, devis_id: int) -> Optional[BonCommande]:
        return self.db.query(BonCommande).filter(BonCommande.devis_id == devis_id).first()

    def find_by_statut(self, statut: StatutBonCommande):
        return self.db.query(BonCommande).filter(BonCommande.statut == statut).all()

    def save(self, data: dict, lignes: list) -> BonCommande:
        bc = BonCommande(**data)
        self.db.add(bc)
        self.db.flush()

        for ligne in lignes:
            l = LigneBonCommande(**ligne, bon_commande_id=bc.id)
            self.db.add(l)

        self.db.commit()
        self.db.refresh(bc)
        return bc

    def update_statut(self, bc: BonCommande, statut: StatutBonCommande) -> BonCommande:
        bc.statut = statut
        self.db.commit()
        self.db.refresh(bc)
        return bc

    def delete(self, bc: BonCommande) -> None:
        self.db.delete(bc)
        self.db.commit()