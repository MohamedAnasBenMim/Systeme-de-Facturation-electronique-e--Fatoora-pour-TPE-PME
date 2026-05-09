from pydantic import BaseModel, Field, validator
from uuid import UUID
from typing import Optional, List
from enum import Enum
from datetime import datetime


class TypeArticle(str, Enum):
    PRODUIT = "PRODUIT"
    SERVICE = "SERVICE"

class CategorieCreate(BaseModel):
    nom:         str
    description: Optional[str] = None
    parent_id:   Optional[int] = None   

class SousCategorieResponse(BaseModel):
    id:          int
    nom:         str
    description: Optional[str]
    parent_id:   Optional[int]

    class Config:
        from_attributes = True


class CategorieResponse(BaseModel):
    id:              int
    nom:             str
    description:     Optional[str]
    parent_id:       Optional[int]
    sous_categories: List[SousCategorieResponse] = []

    class Config:
        from_attributes = True

class UniteMesureCreate(BaseModel):
    nom:  str
    code: str

class UniteMesureResponse(BaseModel):
    id:   int                            
    code: str

    class Config:
        from_attributes = True

class ProduitCreate(BaseModel):
    type:           TypeArticle       = TypeArticle.PRODUIT
    designation:    str               = Field(..., min_length=1)
    reference:      Optional[str]     = None
    code_barre:     Optional[str]     = None
    description:    Optional[str]     = None
    marque:         Optional[str]     = None
    categorie_id:   Optional[int]     = None    
    unite_id:       Optional[int]     = None    
    prix_achat_ht:  float             = Field(0.0, ge=0)
    prix_vente_ht:  float             = Field(0.0, ge=0)
    taxe_id:        Optional[str]     = None    
    groupe_taxe_id: Optional[str]     = None    
    is_stockable:   bool              = True
    est_actif:      bool              = True

class ProduitUpdate(BaseModel):
    designation:    Optional[str]     = None
    reference:      Optional[str]     = None
    code_barre:     Optional[str]     = None
    description:    Optional[str]     = None
    marque:         Optional[str]     = None
    categorie_id:   Optional[int]     = None    
    unite_id:       Optional[int]     = None    
    prix_achat_ht:  Optional[float]   = Field(None, ge=0)
    prix_vente_ht:  Optional[float]   = Field(None, ge=0)
    taxe_id:        Optional[str]     = None    
    groupe_taxe_id: Optional[str]     = None    
    is_stockable:   Optional[bool]    = None
    est_actif:      Optional[bool]    = None

class ProduitResponse(BaseModel):
    id:              int               
    entreprise_id:   int
    type:            TypeArticle
    designation:     str
    reference:       Optional[str]
    code_barre:      Optional[str]
    description:     Optional[str]
    image_url:       Optional[str]
    marque:          Optional[str]
    prix_achat_ht:   float
    prix_vente_ht:   float
    prix_vente_ttc:  Optional[float]
    taxe_id:         Optional[str]     
    groupe_taxe_id:  Optional[str]     
    is_stockable:    bool
    est_actif:       bool
    categorie:       Optional[CategorieResponse]
    unite:           Optional[UniteMesureResponse]
    date_creation:   datetime

    class Config:
        from_attributes = True

class BulkUpdatePrix(BaseModel):
    categorie_id:  Optional[int]   = None    
    pourcentage:   float           = Field(..., description="ex: 5 pour +5%")
    type_prix:     str             = "vente"

class ProduitSearchParams(BaseModel):
    q:            Optional[str]         = None   # recherche plein texte
    type:         Optional[TypeArticle] = None
    categorie_id: Optional[int]         = None    
    est_actif:    Optional[bool]        = True
    is_stockable: Optional[bool]        = None
    page:         int                   = 1
    limit:        int                   = Field(20, le=100)

class ProduitListResponse(BaseModel):
    items: List[ProduitResponse]
    total: int
    page:  int
    pages: int

    class Config:
        from_attributes = True