from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.bc_service import BonCommandeService
from app.schemas.bc_schema import BonCommandeCreate, BonCommandeResponse, BonCommandeListResponse
from app.models.BonCommande import StatutBonCommande
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/bon-commande",
    tags=["Bon de Commande"],
    dependencies=[Depends(get_current_user)]
)


def get_service(db: Session = Depends(get_db)) -> BonCommandeService:
    return BonCommandeService(db)


# ──────────────────────────────────────────────────────────────────────
# CRUD
# ──────────────────────────────────────────────────────────────────────

@router.get("/", response_model=BonCommandeListResponse)
def get_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: BonCommandeService = Depends(get_service)
):
    return service.get_all(page, page_size)

@router.get("/{bc_id}", response_model=BonCommandeResponse)
def get_by_id(bc_id: int, service: BonCommandeService = Depends(get_service)):
    return service.get_by_id(bc_id)

@router.post("/depuis-devis", response_model=BonCommandeResponse, status_code=status.HTTP_201_CREATED)
async def create_depuis_devis(
    payload: BonCommandeCreate,
    service: BonCommandeService = Depends(get_service)
):
    """
    Crée un BC en partant d'un devis existant (payload.devis_id requis).
    Utiliser de préférence POST /devis/{id}/convertir/bon-commande.
    """
    return await service.create_from_devis(payload)

@router.post("/manuel", response_model=BonCommandeResponse, status_code=status.HTTP_201_CREATED)
async def create_manuel(
    payload: BonCommandeCreate,
    service: BonCommandeService = Depends(get_service)
):
    """Crée un BC sans devis source (commande directe)."""
    return await service.create_manuel(payload)

@router.put("/{bc_id}/statut", response_model=BonCommandeResponse)
async def changer_statut(
    bc_id: int,
    statut: StatutBonCommande,
    service: BonCommandeService = Depends(get_service)
):
    return await service.changer_statut(bc_id, statut)


# ──────────────────────────────────────────────────────────────────────
# CONVERSIONS
# ──────────────────────────────────────────────────────────────────────

@router.post("/{bc_id}/convertir/bon-livraison", status_code=status.HTTP_201_CREATED)
def convertir_en_bl(bc_id: int, service: BonCommandeService = Depends(get_service)):
    """
    BC CONFIRMÉ → Bon de livraison.
    Copie toutes les lignes. Le BC passe en EN_COURS.
    """
    return service.convertir_en_bl(bc_id)

@router.post("/{bc_id}/convertir/facture", status_code=status.HTTP_201_CREATED)
async def convertir_en_facture(bc_id: int, service: BonCommandeService = Depends(get_service)):
    """
    BC CONFIRMÉ → Facture directement (sans BL, ex : prestation de service).
    Génère le numéro FAC et appelle le factures-service.
    """
    return await service.convertir_en_facture(bc_id)


# PDF GENERATION

@router.get("/{bc_id}/pdf", response_class=StreamingResponse)
async def generate_bc_pdf(bc_id: int, service: BonCommandeService = Depends(get_service)):
    pdf_bytes = await service.generate_pdf(bc_id)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=bon_commande_{bc_id}.pdf"}
    )