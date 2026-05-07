from fastapi import APIRouter, Depends, status, Query, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.bl_service import BonLivraisonService
from app.schemas.bl_schema import BonLivraisonCreate, BonLivraisonResponse, BonLivraisonListResponse
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/bon-livraison",
    tags=["Bon de Livraison"],
    dependencies=[Depends(get_current_user)]
)


def get_service(db: Session = Depends(get_db)) -> BonLivraisonService:
    return BonLivraisonService(db)


# ──────────────────────────────────────────────────────────────────────
# CRUD
# ──────────────────────────────────────────────────────────────────────

@router.post("/", response_model=BonLivraisonResponse, status_code=201)
async def create(
    payload: BonLivraisonCreate,
    service: BonLivraisonService = Depends(get_service)
):
    return await service.create(payload)

@router.get("/", response_model=BonLivraisonListResponse)
def get_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: BonLivraisonService = Depends(get_service)
):
    return service.get_all(page, page_size)

@router.get("/{bl_id}", response_model=BonLivraisonResponse)
def get_by_id(bl_id: int, service: BonLivraisonService = Depends(get_service)):
    return service.get_by_id(bl_id)

@router.delete("/{bl_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(bl_id: int, service: BonLivraisonService = Depends(get_service)):
    service.delete(bl_id)


# ──────────────────────────────────────────────────────────────────────
# CRÉATION (depuis document source)
# ──────────────────────────────────────────────────────────────────────

@router.post("/depuis-bc/{bc_id}", response_model=BonLivraisonResponse, status_code=status.HTTP_201_CREATED)
async def create_depuis_bc(
    bc_id: int,
    db: Session = Depends(get_db),
    service: BonLivraisonService = Depends(get_service)
):
    """
    BC CONFIRMÉ → Bon de livraison.
    Utiliser de préférence POST /bon-commande/{id}/convertir/bon-livraison.
    """
    return await service.create_from_bon_commande(bc_id, db)

@router.post("/depuis-devis/{devis_id}", response_model=BonLivraisonResponse, status_code=status.HTTP_201_CREATED)
async def create_depuis_devis(
    devis_id: int,
    service: BonLivraisonService = Depends(get_service)
):
    """
    Devis ACCEPTÉ → BL directement (sans BC).
    Utiliser de préférence POST /devis/{id}/convertir/bon-livraison.
    """
    return await service.create_from_devis(devis_id)


# ──────────────────────────────────────────────────────────────────────
# ACTIONS SUR LE BL
# ──────────────────────────────────────────────────────────────────────

@router.post("/convertir/facture-groupee", status_code=status.HTTP_201_CREATED)
async def convertir_groupe_en_facture(
    bl_ids: list[int] = Body(
        ...,
        example=[1, 2, 3],
        description="Liste des IDs de BL LIVRÉS à regrouper dans une seule facture"
    ),
    service: BonLivraisonService = Depends(get_service)
):

    return await service.convertir_groupe_en_facture(bl_ids)

@router.put("/{bl_id}/confirmer", response_model=BonLivraisonResponse)
async def confirmer(bl_id: int, service: BonLivraisonService = Depends(get_service)):
    """
    Confirme la livraison complète. Passe le BL en LIVRÉ.
    Met à jour le BC source si applicable.
    """
    return await service.confirmer_livraison(bl_id)

@router.put("/{bl_id}/annuler", response_model=BonLivraisonResponse)
async def annuler(bl_id: int, service: BonLivraisonService = Depends(get_service)):
    return await service.annuler(bl_id)

@router.put("/{bl_id}/quantites", response_model=BonLivraisonResponse)
async def mettre_a_jour_quantites(
    bl_id: int,
    quantites: dict[int, float] = Body(
        ...,
        example={1: 5.0, 2: 3.0},
        description="Dictionnaire {ligne_id: quantite_livree}"
    ),
    service: BonLivraisonService = Depends(get_service)
):
    """
    Met à jour les quantités livrées ligne par ligne.
    Si certaines quantités < commandées, le BL passe en PARTIEL.
    """
    return await service.mettre_a_jour_quantites_livrees(bl_id, quantites)


# ──────────────────────────────────────────────────────────────────────
# PDF GENERATION
# ──────────────────────────────────────────────────────────────────────

@router.get("/{bl_id}/pdf", response_class=StreamingResponse)
async def generate_bl_pdf(bl_id: int, service: BonLivraisonService = Depends(get_service)):
    pdf_bytes = await service.generate_pdf(bl_id)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=bon_livraison_{bl_id}.pdf"}
    )

@router.post("/{bl_id}/partiel", response_model=BonLivraisonResponse, status_code=status.HTTP_201_CREATED)
async def creer_bl_partiel(bl_id: int, service: BonLivraisonService = Depends(get_service)):
    """
    BL PARTIEL → crée un nouveau BL pour les quantités non livrées (reliquat).
    Confirme le BL parent sur les quantités effectivement livrées.
    Génère un nouveau numéro BL pour le reliquat.
    """
    return await service.creer_bl_partiel(bl_id)




@router.post("/{bl_id}/convertir/facture", status_code=status.HTTP_201_CREATED)
async def convertir_en_facture(bl_id: int, service: BonLivraisonService = Depends(get_service)):
    return await service.convertir_en_facture(bl_id)

