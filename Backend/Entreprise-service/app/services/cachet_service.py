# ms-entreprise/app/services/cachet_service.py
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from app.repositories.cachet_repository import CachetRepository
from app.models.cachet import Cachet

ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/svg+xml"}
MAX_SIZE_BYTES     = 2 * 1024 * 1024  # 2 MB

class CachetService:
    def __init__(self, db: Session):
        self.repo = CachetRepository(db)

    async def upload(self, entreprise_id: int, file: UploadFile, nom: str | None) -> Cachet:
        # Validation type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Format non supporté. Formats acceptés : PNG, JPEG, SVG"
            )

        image_data = await file.read()

        # Validation taille
        if len(image_data) > MAX_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fichier trop volumineux. Maximum 2 MB."
            )

        return self.repo.upsert(
            entreprise_id = entreprise_id,
            image_data    = image_data,
            image_mime    = file.content_type,
            nom           = nom,
        )

    def get(self, entreprise_id: int) -> Cachet:
        cachet = self.repo.get_by_entreprise(entreprise_id)
        if not cachet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun cachet configuré pour cette entreprise"
            )
        return cachet

    def delete(self, entreprise_id: int) -> None:
        deleted = self.repo.delete(entreprise_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun cachet à supprimer"
            )