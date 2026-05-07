# ms-entreprise/app/api/cachet_router.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, Response
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.cachet_service import CachetService
from app.schemas.cachet import CachetResponse, CachetUploadResponse
from app.core.dependencies import get_current_entreprise_id  # ton middleware JWT

router = APIRouter(prefix="/cachet", tags=["Cachet"])

def get_service(db: Session = Depends(get_db)):
    return CachetService(db)

@router.post("", response_model=CachetUploadResponse)
async def upload_cachet(
    file:          UploadFile = File(...),
    nom:           str | None = Form(None),
    entreprise_id: int        = Depends(get_current_entreprise_id),
    service:       CachetService = Depends(get_service),
):
    cachet = await service.upload(entreprise_id, file, nom)
    return CachetUploadResponse(
        message = "Cachet enregistré avec succès",
        cachet  = cachet,
    )

@router.get("", response_model=CachetResponse)
def get_cachet(
    entreprise_id: int = Depends(get_current_entreprise_id),
    service: CachetService = Depends(get_service),
):
    return service.get(entreprise_id)

@router.get("/image")
def get_cachet_image(
    entreprise_id: int = Depends(get_current_entreprise_id),
    service: CachetService = Depends(get_service),
):
    """Retourne l'image brute — utilisable directement dans un <img src=...>"""
    cachet = service.get(entreprise_id)
    return FastAPIResponse(
        content      = cachet.image_data,
        media_type   = cachet.image_mime,
    )

@router.delete("", status_code=204)
def delete_cachet(
    entreprise_id: int = Depends(get_current_entreprise_id),
    service: CachetService = Depends(get_service),
):
    service.delete(entreprise_id)