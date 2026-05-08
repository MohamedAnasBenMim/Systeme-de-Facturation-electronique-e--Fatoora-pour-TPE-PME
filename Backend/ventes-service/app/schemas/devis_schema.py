from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from app.schemas.ligne_devis_schema import LigneDevisResponse, LigneDevisCreate
from app.models.devis import StatutDevis, TypeConversionDevis



class DevisBase(BaseModel):
    date_expiration: date
    montant_total: float = Field(gt=0)
    lignes: List

class DevisCreate(BaseModel):
    client_id: int
    date_expiration: Optional[datetime]
    lignes: List[LigneDevisCreate]
    statut: StatutDevis = StatutDevis.BROUILLON
    taux_remise: float = Field(default=0.0, ge=0, le=100, description="Pourcentage de remise")

class DevisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id                : int
    numero            : str
    client_id         : int
    statut            : StatutDevis
    date_creation     : datetime
    date_expiration   : Optional[datetime] = None
    notes             : Optional[str] = None
    montant_ht        : float
    montant_tva       : float
    montant_ttc       : float
    id_document_cible : Optional[int] = None
    lignes            : List[LigneDevisResponse]