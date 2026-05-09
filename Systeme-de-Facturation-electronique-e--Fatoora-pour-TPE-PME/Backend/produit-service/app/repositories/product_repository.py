from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from app.models.product import Produit, Categorie, UniteMesure, TypeArticle
from app.schemas.product_schema import ProduitCreate, ProduitUpdate, ProduitSearchParams
from typing import List, Optional, Tuple


class ProduitRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── Produits ───────────────────────────────────────────────────────────────
    def search(
        self, entreprise_id: int, params: ProduitSearchParams
    ) -> Tuple[List[Produit], int]:
        q = self.db.query(Produit).filter(
            Produit.entreprise_id == entreprise_id
        )
        if params.est_actif is not None:
            q = q.filter(Produit.est_actif == params.est_actif)
        if params.type:
            q = q.filter(Produit.type == params.type)
        if params.categorie_id:
            q = q.filter(Produit.categorie_id == params.categorie_id)
        if params.is_stockable is not None:
            q = q.filter(Produit.is_stockable == params.is_stockable)

        if params.q:
            term = f"%{params.q}%"
            q = q.filter(or_(
                Produit.designation.ilike(term),
                Produit.reference.ilike(term),
                Produit.code_barre.ilike(term),
                Produit.description.ilike(term),
                Produit.marque.ilike(term),
            ))

        total = q.count()
        items = q.offset((params.page - 1) * params.limit).limit(params.limit).all()
        return items, total

    def get_by_id(self, produit_id: str, entreprise_id: int) -> Optional[Produit]:
        return self.db.query(Produit).filter(
            Produit.id == produit_id,
            Produit.entreprise_id == entreprise_id,
        ).first()

    def get_by_id_simple(self, produit_id: str) -> Optional[Produit]:
        """Récupère un produit par ID seulement (sans entreprise)"""
        return self.db.query(Produit).filter(Produit.id == produit_id).first()

    def reference_exists(self, ref: str, entreprise_id: int, exclude_id: str = None) -> bool:
        q = self.db.query(Produit).filter(
            Produit.reference == ref,
            Produit.entreprise_id == entreprise_id,
        )
        if exclude_id:
            q = q.filter(Produit.id != exclude_id)
        return q.first() is not None

    def create(self, entreprise_id: int, data: dict, ttc: float) -> Produit:
        p = Produit(
            entreprise_id  = entreprise_id,
            prix_vente_ttc = ttc,
            **data,
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def update(self, produit: Produit, data: dict, ttc: float = None) -> Produit:
        for k, v in data.items():
            if v is not None:
                setattr(produit, k, v)
        if ttc is not None:
            produit.prix_vente_ttc = ttc
        self.db.commit()
        self.db.refresh(produit)
        return produit

    def delete(self, produit: Produit) -> None:
        produit.est_actif = False
        self.db.commit()

    def hard_delete(self, produit: Produit) -> None:
        self.db.delete(produit)
        self.db.commit()

    def bulk_update_prix(
        self,
        entreprise_id: int,
        pourcentage: float,
        type_prix: str,
        categorie_id: int = None,
    ) -> int:
        q = self.db.query(Produit).filter(
            Produit.entreprise_id == entreprise_id,
            Produit.est_actif == True,
        )
        if categorie_id:
            q = q.filter(Produit.categorie_id == categorie_id)

        produits = q.all()
        facteur = 1 + (pourcentage / 100)

        for p in produits:
            if type_prix == "vente":
                p.prix_vente_ht = round(p.prix_vente_ht * facteur, 3)
            else:
                p.prix_achat_ht = round(p.prix_achat_ht * facteur, 3)

        self.db.commit()
        return len(produits)

    def get_stockables(self, entreprise_id: int) -> List[Produit]:
        return self.db.query(Produit).filter(
            Produit.entreprise_id == entreprise_id,
            Produit.is_stockable == True,
            Produit.est_actif == True,
        ).all()

    def get_categories(self, entreprise_id: int) -> List[Categorie]:
        return self.db.query(Categorie).options(
            joinedload(Categorie.sous_categories)
        ).filter(
            Categorie.entreprise_id == entreprise_id,
        ).all()

    def create_categorie(self, entreprise_id: int, data: dict) -> Categorie:
        c = Categorie(entreprise_id=entreprise_id, **data)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c

    def delete_categorie(self, categorie_id: int, entreprise_id: int) -> bool:
        c = self.db.query(Categorie).filter(
            Categorie.id == categorie_id,
            Categorie.entreprise_id == entreprise_id,
        ).first()
        if not c:
            return False
        self.db.delete(c)
        self.db.commit()
        return True

    # ── Unités ─────────────────────────────────────────────────────────────────
    def get_unites(self, entreprise_id: int) -> List[UniteMesure]:
        return self.db.query(UniteMesure).filter(
            UniteMesure.entreprise_id == entreprise_id
        ).all()

    def create_unite(self, entreprise_id: int, data: dict) -> UniteMesure:
        u = UniteMesure(entreprise_id=entreprise_id, **data)
        self.db.add(u)
        self.db.commit()
        self.db.refresh(u)
        return u