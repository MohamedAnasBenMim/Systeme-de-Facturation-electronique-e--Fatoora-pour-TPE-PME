from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.devis_schema import DevisCreate, DevisResponse
from app.services.devis_service import DevisService
from app.models.devis import StatutDevis
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/devis",
    tags=["Devis"],
    dependencies=[Depends(get_current_user)]
)


def get_service(db: Session = Depends(get_db)) -> DevisService:
    return DevisService(db)


# CRUD

@router.post("/", response_model=DevisResponse, status_code=status.HTTP_201_CREATED)
def create_devis(payload: DevisCreate, service: DevisService = Depends(get_service)):
    return service.create(payload)

@router.get("/", response_model=list[DevisResponse])
def get_all(service: DevisService = Depends(get_service)):
    return service.get_all()

@router.get("/{devis_id}", response_model=DevisResponse)
def get_by_id(devis_id: int, service: DevisService = Depends(get_service)):
    return service.get_one(devis_id)

@router.delete("/{devis_id}", response_model=DevisResponse)
def delete(devis_id: int, service: DevisService = Depends(get_service)):
    return service.delete(devis_id)


# ──────────────────────────────────────────────────────────────────────
# WORKFLOW — Statuts
# ──────────────────────────────────────────────────────────────────────

@router.put("/{devis_id}/envoyer", response_model=DevisResponse)
def envoyer(devis_id: int, service: DevisService = Depends(get_service)):
    """BROUILLON → ENVOYÉ"""
    return service.envoyer_devis(devis_id)

@router.put("/{devis_id}/accepter", response_model=DevisResponse)
def accepter(devis_id: int, service: DevisService = Depends(get_service)):
    """ENVOYÉ → ACCEPTÉ"""
    return service.accepter_devis(devis_id)

@router.put("/{devis_id}/refuser", response_model=DevisResponse)
def refuser(devis_id: int, service: DevisService = Depends(get_service)):
    """ENVOYÉ → REFUSÉ"""
    return service.refuser_devis(devis_id)

@router.put("/{devis_id}/statut", response_model=DevisResponse)
def update_statut(devis_id: int, statut: StatutDevis, service: DevisService = Depends(get_service)):
    return service.update_statut(devis_id, statut)


# CONVERSIONS
# ──────────────────────────────────────────────────────────────────────

@router.post("/{devis_id}/convertir/bon-commande", status_code=status.HTTP_201_CREATED)
def convertir_en_bc(devis_id: int, service: DevisService = Depends(get_service)):
    """
    Devis ACCEPTÉ → Bon de commande.
    Crée un BC avec les mêmes lignes, passe le devis en CONVERTI.
    """
    return service.convertir_en_bc(devis_id)

@router.post("/{devis_id}/convertir/bon-livraison", status_code=status.HTTP_201_CREATED)
def convertir_en_bl(devis_id: int, service: DevisService = Depends(get_service)):
    """
    Devis ACCEPTÉ → Bon de livraison directement (sans BC intermédiaire).
    Passe le devis en CONVERTI.
    """
    return service.convertir_en_bl(devis_id)

@router.post("/{devis_id}/convertir/facture", status_code=status.HTTP_201_CREATED)
async def convertir_en_facture(devis_id: int, service: DevisService = Depends(get_service)):
  
    return await service.convertir_en_facture(devis_id)


# PDF GENERATION
# ──────────────────────────────────────────────────────────────────────

@router.get("/{devis_id}/pdf", response_class=StreamingResponse)
async def generate_devis_pdf(devis_id: int, service: DevisService = Depends(get_service)):
    pdf_bytes = await service.generate_pdf(devis_id)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=devis_{devis_id}.pdf"}
    )