from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.models.product import CategoryEnum
from app.Core.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"], dependencies=[Depends(get_current_user)])

def get_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.get("/", response_model=ProductListResponse)
def get_all(
    search: Optional[str] = Query(None, description="Recherche par nom ou description"),
    categorie: Optional[CategoryEnum] = Query(None, description="Filtrer par catégorie"),
    prix_min: Optional[float] = Query(None, description="Prix minimum"),
    prix_max: Optional[float] = Query(None, description="Prix maximum"),
    quantite_min: Optional[int] = Query(None, description="Quantité minimum"),
    en_stock: Optional[bool] = Query(None, description="Uniquement les produits en stock"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(10, ge=1, le=100, description="Nombre d'éléments par page"),
    service: ProductService = Depends(get_service)
):
    return service.get_all(
        search=search,
        categorie=categorie,
        prix_min=prix_min,
        prix_max=prix_max,
        quantite_min=quantite_min,
        en_stock=en_stock,
        page=page,
        page_size=page_size
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_by_id(product_id: int, service: ProductService = Depends(get_service)):
    return service.get_by_id(product_id)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create(payload: ProductCreate, service: ProductService = Depends(get_service)):
    return service.create(payload)

@router.put("/{product_id}", response_model=ProductResponse)
def update(product_id: int, payload: ProductUpdate, service: ProductService = Depends(get_service)):
    return service.update(product_id, payload)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(product_id: int, service: ProductService = Depends(get_service)):
    service.delete(product_id)