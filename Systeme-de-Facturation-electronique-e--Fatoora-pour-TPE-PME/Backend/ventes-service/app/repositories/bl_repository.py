from sqlalchemy.orm import Session
from typing import Optional
from app.models.BonLivraison import BonLivraison, StatutBonLivraison
from app.models.ligne_livraison import LigneBonLivraison
from datetime import datetime, timezone

class BonLivraisonRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_all(self, page: int = 1, page_size: int = 10):
        query = self.db.query(BonLivraison)\
                    .order_by(BonLivraison.date_creation.desc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    def find_by_id(self, bl_id: int) -> Optional[BonLivraison]:
        return self.db.query(BonLivraison)\
                    .filter(BonLivraison.id == bl_id).first()

    def find_by_bon_commande(self, bc_id: int) -> Optional[BonLivraison]:
        return self.db.query(BonLivraison)\
                    .filter(BonLivraison.bon_commande_id == bc_id).first()

    def find_by_statut(self, statut: StatutBonLivraison):
        return self.db.query(BonLivraison)\
                    .filter(BonLivraison.statut == statut).all()

    def find_by_client(self, client_id: int):
        return self.db.query(BonLivraison)\
                    .filter(BonLivraison.client_id == client_id).all()

    def save(self, data: dict, lignes: list) -> BonLivraison:
        bl = BonLivraison(**data)
        self.db.add(bl)
        self.db.flush()

        for ligne in lignes:
            l = LigneBonLivraison(**ligne, bon_livraison_id=bl.id)
            self.db.add(l)

        self.db.commit()
        self.db.refresh(bl)
        return bl

    def update_statut(
        self,
        bl: BonLivraison,
        statut: StatutBonLivraison,
        date_livraison: bool = False
    ) -> BonLivraison:
        bl.statut = statut
        if date_livraison:
            bl.date_livraison_reelle = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(bl)
        return bl

    def update_expedition(self, bl: BonLivraison) -> BonLivraison:
        bl.statut = StatutBonLivraison.EXPEDIE
        bl.date_expedition = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(bl)
        return bl
    
    def update(self, bl) -> None:
        self.db.commit()
        self.db.refresh(bl)
        return bl

    def delete(self, bl: BonLivraison) -> None:
        self.db.delete(bl)
        self.db.commit()