from fastapi import (
    APIRouter, Depends, status, UploadFile,
    File, Query, Request
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.product_service import ProduitService
from app.schemas.product_schema import (
    ProduitCreate, ProduitUpdate, ProduitResponse, ProduitListResponse,  # ← ajout ProduitListResponse
    CategorieCreate, CategorieResponse,
    UniteMesureCreate, UniteMesureResponse,
    BulkUpdatePrix, ProduitSearchParams, TypeArticle
)
from app.Core.dependencies import get_current_entreprise_id
from typing import List, Optional
import io

router = APIRouter(prefix="/produits", tags=["Catalogue Produits"])


def get_service(db: Session = Depends(get_db)):
    return ProduitService(db)


def get_token(request: Request) -> str:
    return request.headers.get("Authorization", "").replace("Bearer ", "")


# ══════════════════════════════════════════════════════
# CATÉGORIES
# ══════════════════════════════════════════════════════

@router.get("/categories", response_model=List[CategorieResponse])
def list_categories(
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return service.list_categories(int(entreprise_id))


@router.post("/categories", response_model=CategorieResponse, status_code=201)
def create_categorie(
    data: CategorieCreate,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return service.create_categorie(int(entreprise_id), data)


@router.delete("/categories/{categorie_id}", status_code=204)
def delete_categorie(
    categorie_id: int,  # ← int au lieu de str
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    service.delete_categorie(int(entreprise_id), categorie_id)


# ══════════════════════════════════════════════════════
# UNITÉS DE MESURE
# ══════════════════════════════════════════════════════

@router.get("/unites", response_model=List[UniteMesureResponse])
def list_unites(
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return service.list_unites(int(entreprise_id))


@router.post("/unites", response_model=UniteMesureResponse, status_code=201)
def create_unite(
    data: UniteMesureCreate,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return service.create_unite(int(entreprise_id), data)


# ══════════════════════════════════════════════════════
# BULK OPERATIONS
# ══════════════════════════════════════════════════════

@router.patch("/bulk/prix")
def bulk_update_prix(
    data: BulkUpdatePrix,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return service.bulk_update_prix(int(entreprise_id), data)


@router.post("/import")
async def import_csv(
    file: UploadFile = File(...),
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
    request: Request = None,
):
    if not file.filename.endswith(".csv"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Fichier CSV uniquement")
    return await service.import_csv(int(entreprise_id), file, get_token(request))


@router.get("/export")
def export_csv(
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    csv_content = service.export_csv(int(entreprise_id))
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=catalogue.csv"},
    )


@router.get("/stockables")
def get_stockables(
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return service.get_stockables(int(entreprise_id))


# ══════════════════════════════════════════════════════
# CRUD PRODUIT
# ══════════════════════════════════════════════════════

@router.get("", response_model=ProduitListResponse)  # ← plus dict
def list_produits(
    q:            Optional[str]         = Query(None),
    type:         Optional[TypeArticle] = Query(None),
    categorie_id: Optional[int]         = Query(None),
    est_actif:    Optional[bool]        = Query(True),
    is_stockable: Optional[bool]        = Query(None),
    page:         int                   = Query(1, ge=1),
    limit:        int                   = Query(20, le=100),
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    params = ProduitSearchParams(
        q=q, type=type, categorie_id=categorie_id,
        est_actif=est_actif, is_stockable=is_stockable,
        page=page, limit=limit,
    )
    return service.list(int(entreprise_id), params)


@router.post("", response_model=ProduitResponse, status_code=201)
async def create_produit(
    data: ProduitCreate,
    request: Request,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return await service.create(int(entreprise_id), data, get_token(request))


@router.get("/{produit_id}", response_model=ProduitResponse)
def get_produit(
    produit_id: int,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return service.get(int(entreprise_id), produit_id)



@router.get("/internal/{produit_id}")
def get_produit_internal(
    produit_id: int,
    service: ProduitService = Depends(get_service),
):
    # Recherche sans entreprise_id (pour appels internes)
    p = service.get_by_id_only(produit_id)
    return {"designation": p.designation or f"Produit #{produit_id}"}


@router.patch("/{produit_id}", response_model=ProduitResponse)
async def update_produit(
    produit_id: int,  
    data: ProduitUpdate,
    request: Request,
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    return await service.update(int(entreprise_id), produit_id, data, get_token(request))


@router.delete("/{produit_id}", status_code=204)
def delete_produit(
    produit_id: int,  
    entreprise_id: str = Depends(get_current_entreprise_id),
    service: ProduitService = Depends(get_service),
):
    service.delete(int(entreprise_id), produit_id)


from fastapi.responses import FileResponse
import os

@router.get("/static/produits/{entreprise_id}/{filename}")
def get_image(entreprise_id: int, filename: str):
    path = f"static/produits/{entreprise_id}/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image introuvable")
    return FileResponse(path)