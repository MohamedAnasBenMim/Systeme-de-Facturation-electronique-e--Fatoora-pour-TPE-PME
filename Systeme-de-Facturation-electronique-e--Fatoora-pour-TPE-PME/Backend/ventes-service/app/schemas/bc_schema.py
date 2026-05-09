from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.models.BonCommande import StatutBonCommande


class LigneBonCommandeCreate(BaseModel):
    product_id    : int
    description   : Optional[str] = None
    quantite      : float = Field(..., gt=0)
    prix_unitaire : float = Field(..., gt=0)
    taux_tva      : float = Field(default=20.0, ge=0)
    montant_ht    : float = Field(default=0.0)


class LigneBonCommandeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id              : int
    product_id      : int
    description     : Optional[str] = None
    quantite        : float
    quantite_livree : float
    prix_unitaire   : float
    taux_tva        : float
    montant_ht      : float


class BonCommandeCreate(BaseModel):
    client_id                : int
    devis_id                 : Optional[int] = None        
    date_livraison_souhaitee : Optional[datetime] = None   
    notes                    : Optional[str] = None
    lignes                   : List[LigneBonCommandeCreate]


class BonCommandeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id                       : int
    numero                   : str                         
    client_id                : int
    devis_id                 : Optional[int] = None
    statut                   : StatutBonCommande
    date_creation            : datetime
    date_livraison_souhaitee : Optional[datetime] = None  
    notes                    : Optional[str] = None
    montant_ht               : float
    montant_tva              : float
    montant_ttc              : float
    lignes                   : List[LigneBonCommandeResponse]


class BonCommandeListResponse(BaseModel):
    total     : int
    page      : int
    page_size : int
    items     : List[BonCommandeResponse]