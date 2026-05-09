# app/schemas/depense.py
from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.models.depense import CategorieDepense, StatutDepense

class DepenseCreate(BaseModel):
    product_id:    Optional[int] = None
    designation:  str
    categorie:    CategorieDepense
    montant:      float
    statut:       StatutDepense = StatutDepense.EN_ATTENTE
    date_depense: date
    fournisseur:  Optional[str] = None
    notes:        Optional[str] = None

class DepenseRead(DepenseCreate):
    id:            int
    entreprise_id: int

    class Config:
        from_attributes = True