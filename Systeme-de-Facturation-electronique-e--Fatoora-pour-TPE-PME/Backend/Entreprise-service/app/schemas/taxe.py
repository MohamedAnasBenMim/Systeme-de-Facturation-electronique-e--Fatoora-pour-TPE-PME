# ms-entreprise/app/schemas/taxe.py
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List

# ── Taxe ──────────────────────────────────────────────────
class TaxeCreate(BaseModel):
    nom:         str          = Field(..., example="TVA")
    code:        str          = Field(..., example="TVA_19")
    taux:        float        = Field(..., ge=0, le=100, example=19.0)
    description: str | None  = None
    est_active:  bool         = True
    est_defaut:  bool         = False

class TaxeUpdate(BaseModel):
    nom:         str | None   = None
    taux:        float | None = Field(None, ge=0, le=100)
    description: str | None   = None
    est_active:  bool | None  = None
    est_defaut:  bool | None  = None

class TaxeResponse(BaseModel):
    id:            UUID
    entreprise_id: int
    nom:           str
    code:          str
    taux:          float
    description:   str | None
    est_active:    bool
    est_defaut:    bool

    class Config:
        from_attributes = True

# ── Groupe de Taxes ────────────────────────────────────────
class GroupeTaxeCreate(BaseModel):
    nom:         str
    description: str | None = None
    taxe_ids:    List[UUID]  = Field(..., min_items=1)

class GroupeTaxeUpdate(BaseModel):
    nom:         str | None   = None
    description: str | None   = None
    taxe_ids:    List[UUID] | None = None
    est_actif:   bool | None  = None

class GroupeTaxeResponse(BaseModel):
    id:            UUID
    entreprise_id: int
    nom:           str
    description:   str | None
    est_actif:     bool
    taxes:         List[TaxeResponse] = []
    taux_total:    float = 0.0         

    class Config:
        from_attributes = True