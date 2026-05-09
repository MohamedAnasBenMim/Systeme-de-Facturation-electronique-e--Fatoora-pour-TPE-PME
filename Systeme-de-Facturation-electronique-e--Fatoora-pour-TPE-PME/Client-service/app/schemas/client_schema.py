from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class ClientBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    matricule_fiscal: Optional[str] = None

    @field_validator("nom", "prenom")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()


class ClientCreate(ClientBase):
    """Schéma pour la création d'un client (POST)."""
    pass


class ClientUpdate(ClientBase):
    """Schéma pour la mise à jour d'un client (PUT)."""
    pass


class ClientResponse(ClientBase):
    """Schéma de réponse — inclut l'ID."""
    id: int

    model_config = {"from_attributes": True}


class ClientListResponse(BaseModel):
    total: int
    clients: list[ClientResponse]