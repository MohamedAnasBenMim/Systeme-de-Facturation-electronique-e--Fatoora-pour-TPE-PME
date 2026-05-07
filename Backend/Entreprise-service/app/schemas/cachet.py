# ms-entreprise/app/schemas/cachet.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class CachetResponse(BaseModel):
    id:            UUID
    entreprise_id: int
    nom:           str | None
    image_mime:    str
    created_at:    datetime
    updated_at:    datetime

    class Config:
        from_attributes = True

class CachetUploadResponse(BaseModel):
    message: str
    cachet:  CachetResponse