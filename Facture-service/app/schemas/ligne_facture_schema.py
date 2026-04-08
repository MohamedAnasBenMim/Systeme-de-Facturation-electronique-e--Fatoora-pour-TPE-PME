from pydantic import BaseModel

class LigneFactureCreate(BaseModel):
    produit: str
    quantite: int
    prix_unitaire: float

class LigneFactureResponse(LigneFactureCreate):
    id: int

    class Config:
        from_attributes = True