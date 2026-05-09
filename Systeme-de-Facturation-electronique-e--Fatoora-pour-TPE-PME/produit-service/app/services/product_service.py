from sqlalchemy.orm import Session
from typing import Optional
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductListResponse, ProductResponse
from app.models.product import CategoryEnum
import math

class ProductService:

    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def get_all(
        self,
        search: Optional[str] = None,
        categorie: Optional[CategoryEnum] = None,
        prix_min: Optional[float] = None,
        prix_max: Optional[float] = None,
        quantite_min: Optional[int] = None,
        en_stock: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> ProductListResponse:

        total, items = self.repository.find_all_filtered(
            search=search,
            categorie=categorie,
            prix_min=prix_min,
            prix_max=prix_max,
            quantite_min=quantite_min,
            en_stock=en_stock,
            page=page,
            page_size=page_size
        )

        return ProductListResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
            items=[ProductResponse.model_validate(item) for item in items] 
        )

    def get_by_id(self, product_id: int):
        product = self.repository.find_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        return product

    def create(self, product: ProductCreate):
        return self.repository.save(product)

    def update(self, product_id: int, data: ProductUpdate):
        product = self.get_by_id(product_id)
        return self.repository.update(product, data)

    def delete(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        self.repository.delete(product)