from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.repositories.entreprise_repository import EntrepriseRepository
from app.schemas.entreprise_schema import (
    EntrepriseCreate, EntrepriseUpdate,
    EntrepriseResponse, EntrepriseConfigResponse
)
import shutil, os, uuid


class EntrepriseService:

    def __init__(self, db: Session):
        self.repository = EntrepriseRepository(db)

    def create(self, data: EntrepriseCreate, owner_id: int) -> EntrepriseResponse:
        if self.repository.find_by_owner_id(owner_id):
            raise HTTPException(
                status_code=400,
                detail="Vous avez déjà un profil entreprise"
            )
        entreprise_data          = data.model_dump()
        entreprise_data["owner_id"] = owner_id
        return EntrepriseResponse.model_validate(
            self.repository.save(entreprise_data)
        )

    def get_mon_profil(self, owner_id: int) -> EntrepriseResponse:
        e = self.repository.find_by_owner_id(owner_id)
        if not e:
            raise HTTPException(
                status_code=404,
                detail="Profil introuvable — créez votre profil d'abord"
            )
        return EntrepriseResponse.model_validate(e)

    def get_by_id(self, entreprise_id: int) -> EntrepriseResponse:
        e = self.repository.find_by_id(entreprise_id)
        if not e:
            raise HTTPException(status_code=404, detail="Entreprise introuvable")
        return EntrepriseResponse.model_validate(e)

    def get_config(self, entreprise_id: int) -> EntrepriseConfigResponse:
        e = self.repository.find_by_id(entreprise_id)
        if not e:
            raise HTTPException(status_code=404, detail="Entreprise introuvable")
        return EntrepriseConfigResponse.model_validate(e)

    def update(self, data: EntrepriseUpdate, owner_id: int) -> EntrepriseResponse:
        e = self.repository.find_by_owner_id(owner_id)
        if not e:
            raise HTTPException(status_code=404, detail="Profil introuvable")
        return EntrepriseResponse.model_validate(
            self.repository.update(e, data.model_dump(exclude_none=True))
        )

    def upload_logo(self, file: UploadFile, owner_id: int) -> EntrepriseResponse:
     e = self.repository.find_by_owner_id(owner_id)
     if not e:
        raise HTTPException(status_code=404, detail="Profil introuvable")

     if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Format invalide — JPG, PNG ou WebP uniquement"
        )

     os.makedirs("static/logos", exist_ok=True)

     ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "png"
     filename = f"{uuid.uuid4()}.{ext}"
     filepath = f"static/logos/{filename}"

     with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

     logo_url = f"http://localhost:8000/static/logos/{filename}"
     updated = self.repository.update_logo(e, logo_url)

     return EntrepriseResponse.model_validate(updated)