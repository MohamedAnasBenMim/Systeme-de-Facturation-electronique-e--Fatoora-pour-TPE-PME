from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from app.models.client import TypeClient


class ClientBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    matricule_fiscal: Optional[str] = None
    type_client: TypeClient = TypeClient.PARTICULIER
    secteur: Optional[str] = None
    tags: list[str] = []
    niveau: Literal["STANDARD", "VIP"] = "STANDARD"
    is_active: bool = True

    @field_validator("nom", "prenom")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Ce champ ne peut pas etre vide")
        return v.strip()

    @field_validator("telephone")
    @classmethod
    def normalize_telephone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        out = v.strip()
        return out or None

    @field_validator("matricule_fiscal")
    @classmethod
    def normalize_mf(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        out = v.strip().upper()
        return out or None

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list[str]:
        cleaned = []
        for t in v:
            s = t.strip().lower()
            if s and s not in cleaned:
                cleaned.append(s)
        return cleaned


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: int

    model_config = {"from_attributes": True}


class ClientListResponse(BaseModel):
    total: int
    clients: list[ClientResponse]


class PotentialDuplicateResponse(BaseModel):
    client_id: int
    score: int
    reasons: list[str]
    client: ClientResponse
