from pydantic import BaseModel,Field

class LigneDevisCreate(BaseModel):
    product_id: int
    quantite: int
    prix_unitaire: float
    montant_tva           : float = Field(default=20.0, ge=0)
    montant_ht         : float = Field(default=0.0)


class LigneDevisResponse(LigneDevisCreate):
    id: int

    class Config:
        from_attributes = True