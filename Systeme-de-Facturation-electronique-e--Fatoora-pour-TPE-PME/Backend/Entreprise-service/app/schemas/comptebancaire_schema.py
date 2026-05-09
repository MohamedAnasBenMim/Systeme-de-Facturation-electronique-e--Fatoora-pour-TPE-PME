# app/schemas/comptebancaire_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompteBancaireCreate(BaseModel):
    # entreprise_id retiré du body : il est injecté depuis le token JWT côté service
    banque  : str
    agence  : Optional[str] = None
    rib     : str
    iban    : Optional[str] = None
    swift   : Optional[str] = None
    devise  : Optional[str] = "TND"


class CompteBancaireUpdate(BaseModel):
    banque  : Optional[str] = None
    agence  : Optional[str] = None
    rib     : Optional[str] = None
    iban    : Optional[str] = None
    swift   : Optional[str] = None
    devise  : Optional[str] = None


class CompteBancaireResponse(BaseModel):
    id            : int
    entreprise_id : int
    banque        : str
    agence        : Optional[str]
    rib           : str
    iban          : Optional[str]
    swift         : Optional[str]
    devise        : str
    date_creation : datetime

    class Config:
        from_attributes = True