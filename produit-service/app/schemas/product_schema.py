from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.product import CategoryEnum

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    prix: float
    quantite: Optional[int] = 0
    categorie: CategoryEnum = CategoryEnum.AUTRE

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = Field(None, gt=0)
    quantite: Optional[int] = Field(None, ge=0)
    categorie: Optional[CategoryEnum] = None

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    prix: float
    quantite: int
    categorie: CategoryEnum

class ProductListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[ProductResponse]

class Config:
        from_attributes = True