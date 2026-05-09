from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.models.product import Product, CategoryEnum
from app.schemas.product_schema import ProductCreate, ProductUpdate

class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_all_filtered(
        self,
        search: Optional[str] = None,
        categorie: Optional[CategoryEnum] = None,
        prix_min: Optional[float] = None,
        prix_max: Optional[float] = None,
        quantite_min: Optional[int] = None,
        en_stock: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ):
        query = self.db.query(Product)

        #  Recherche par nom ou description
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )

        # Filtre par catégorie
        if categorie:
            query = query.filter(Product.categorie == categorie)

        # Filtre par prix
        if prix_min is not None:
            query = query.filter(Product.prix >= prix_min)
        if prix_max is not None:
            query = query.filter(Product.prix <= prix_max)

        # Filtre par quantité minimale
        if quantite_min is not None:
            query = query.filter(Product.quantite >= quantite_min)

        # Filtre en stock uniquement
        if en_stock is True:
            query = query.filter(Product.quantite > 0)
        elif en_stock is False:
            query = query.filter(Product.quantite == 0)

        #Total avant pagination
        total = query.count()

        #Pagination
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return total, items

    def find_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def save(self, product: ProductCreate) -> Product:
        db_product = Product(**product.model_dump())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update(self, product: Product, data: ProductUpdate) -> Product:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()