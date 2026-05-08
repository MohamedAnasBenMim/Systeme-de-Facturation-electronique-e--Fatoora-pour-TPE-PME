from pydantic import BaseModel, Field
from typing import Optional


class LigneFactureCreate(BaseModel):
    product_id:    int
    description:   Optional[str] = None
    quantite:      float = Field(..., gt=0, description="Quantite doit etre > 0")
    prix_unitaire: float = Field(..., gt=0, description="Prix unitaire doit etre > 0")


class LigneFactureResponse(BaseModel):
    id:            int
    product_id:    int
    designation:   str
    quantite:      float
    prix_unitaire: float
    montant_ligne: float

    class Config:
        from_attributes = True
