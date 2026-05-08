from pydantic import BaseModel

class LigneDevisCreate(BaseModel):
    produit: str
    quantite: int
    prix_unitaire: float

class LigneDevisResponse(LigneDevisCreate):
    id: int

    class Config:
        from_attributes = True