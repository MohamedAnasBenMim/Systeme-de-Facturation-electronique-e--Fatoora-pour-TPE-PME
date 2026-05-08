from pydantic import BaseModel
from typing import List
from .ligne_facture_schema import LigneFactureCreate, LigneFactureResponse

class FactureCreate(BaseModel):
    client: str
    lignes: List[LigneFactureCreate]

class FactureResponse(BaseModel):
    id: int
    client: str
    total_ht: float
    tva: float
    total_ttc: float
    lignes: List[LigneFactureResponse]

    class Config:
        from_attributes = True