from pydantic import BaseModel, Field
from datetime import date
from enum import Enum
from typing import List, Optional
from app.schemas.ligne_devis_schema import LigneDevisResponse,LigneDevisCreate

class StatutDevis(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    BROUILLON = "BROUILLON"
    REFUSE = "REFUSE"
    EXPIRE = "EXPIRE"

class DevisBase(BaseModel):
    date_expiration: date
    montant_total: float = Field(gt=0)
    lignes: List

class DevisCreate(BaseModel):
    client: str
    date_validite: Optional[date]
    lignes: List[LigneDevisCreate]
    statut: StatutDevis = StatutDevis.BROUILLON

class DevisResponse(BaseModel):
    id: int
    client: str
    date_creation: date
    date_validite: Optional[date]
    statut: str
    total_ht: float
    tva: float
    total_ttc: float
    lignes: List[LigneDevisResponse]

    class Config:
        from_attributes = True