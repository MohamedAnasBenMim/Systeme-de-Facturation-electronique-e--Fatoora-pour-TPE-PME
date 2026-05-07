from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from app.models.facture import StatutFacture
from app.schemas.ligne_facture_schema import LigneFactureCreate, LigneFactureResponse


# ---------- CREATE ----------
class FactureCreate(BaseModel):
    numero_facture: Optional[str]  = None   # Optionnel, généré automatiquement si absent
    client_id:      int
    entreprise_id:  int
    date_echeance:  Optional[date] = None
    lignes:         List[LigneFactureCreate]
    source:         Optional[str]  = None   # "DEVIS", "BC", "BL", "MANUEL"
    source_id:      Optional[int]  = None   # id du document source


# ---------- UPDATE ----------
class FactureUpdate(BaseModel):
    date_echeance:  Optional[date] = None
    statut:         Optional[StatutFacture] = None
    lignes:         Optional[List[LigneFactureCreate]] = None


# ---------- RESPONSE ----------
class FactureResponse(BaseModel):
    id:             int
    client_id:      int
    entreprise_id:  int
    total_ht:       float
    tva:            float
    timbre_fiscal:  float
    total_ttc:      float
    date_creation:  date
    date_echeance:  Optional[date]
    statut:         StatutFacture
    pdf_path:       Optional[str]
    lignes:         List[LigneFactureResponse]

    class Config:
        from_attributes = True


# ---------- RESPONSE ENRICHIE (avec données des microservices) ----------
class FactureDetailResponse(BaseModel):
    facture:    FactureResponse
    client:     dict        # données complètes du client
    entreprise: dict        # données complètes de l'entreprise