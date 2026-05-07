from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.models.BonLivraison import StatutBonLivraison, SourceBonLivraison


# ── LIGNES ────────────────────────────────────────────────────

class LigneBonLivraisonCreate(BaseModel):
    product_id         : int
    description        : Optional[str] = None
    quantite           : float = Field(..., gt=0)
    quantite_livree    : float = Field(..., gt=0)
    prix_unitaire      : float = Field(..., gt=0)
    taux_tva           : float = Field(default=20.0, ge=0)
    remise             : float = Field(default=0.0, ge=0)
    montant_ht         : float = Field(default=0.0)


class LigneBonLivraisonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id                 : int
    product_id         : int
    description        : Optional[str] = None
    quantite           : float
    quantite_livree    : float
    prix_unitaire      : float
    taux_tva           : float
    montant_ht         : float


# ── BON DE LIVRAISON ──────────────────────────────────────────

class BonLivraisonCreate(BaseModel):
    client_id          : int
    notes              : Optional[str] = None
    date_livraison     : Optional[datetime] = None
    lignes             : List[LigneBonLivraisonCreate]


class BonLivraisonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id                 : int
    numero             : str                        # BonLivraison.numero
    client_id          : int
    bc_id              : Optional[int] = None       # ForeignKey nullable
    devis_id           : Optional[int] = None       # ForeignKey nullable
    bl_parent_id       : Optional[int] = None
    source             : SourceBonLivraison
    statut             : StatutBonLivraison
    date_creation      : datetime
    date_livraison     : Optional[datetime] = None
    notes              : Optional[str] = None
    facture_id_externe : Optional[int] = None
    montant_ht         : float
    montant_tva        : float
    montant_ttc        : float
    lignes             : List[LigneBonLivraisonResponse]


class BonLivraisonListResponse(BaseModel):
    total      : int
    page       : int
    page_size  : int
    items      : List[BonLivraisonResponse]