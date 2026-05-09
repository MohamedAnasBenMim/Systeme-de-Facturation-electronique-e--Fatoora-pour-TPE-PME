from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime


# ============ FOURNISSEUR ============

class FournisseurCreate(BaseModel):
    nom: str
    matricule_fiscal: str
    adresse: str
    ville: str
    code_postal: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    contact_principal: Optional[str] = None
    delai_paiement_jours: int = 30
    escompte_pourcent: float = 0.0
    seuil_tolerance_quantite: float = 5.0
    seuil_tolerance_prix: float = 5.0


class FournisseurUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    contact_principal: Optional[str] = None
    delai_paiement_jours: Optional[int] = None
    actif: Optional[bool] = None


class FournisseurResponse(BaseModel):
    id: int
    nom: str
    matricule_fiscal: str
    adresse: str
    ville: str
    telephone: Optional[str]
    email: Optional[str]
    actif: bool
    date_creation: datetime

    class Config:
        from_attributes = True


# ============ LIGNE BON DE COMMANDE ============

class LigneBonCommandeCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    designation: str
    reference_fournisseur: Optional[str] = None
    quantite_commandee: int = Field(..., gt=0)
    prix_unitaire: float = Field(..., gt=0)

    @validator("quantite_commandee", "prix_unitaire")
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("Les quantités et prix doivent être positifs")
        return v


class LigneBonCommandeResponse(BaseModel):
    id: int
    product_id: int
    designation: str
    quantite_commandee: int
    quantite_receptionnable: int
    quantite_receptionnee: int
    prix_unitaire: float
    montant_ligne: float

    class Config:
        from_attributes = True


# ============ BON DE COMMANDE ============

class BonCommandeCreate(BaseModel):
    fournisseur_id: int = Field(..., gt=0)
    entreprise_id: int = Field(..., gt=0)
    date_livraison_attendue: Optional[date] = None
    lignes: List[LigneBonCommandeCreate] = Field(..., min_items=1)
    notes: Optional[str] = None


class BonCommandeUpdate(BaseModel):
    date_livraison_attendue: Optional[date] = None
    notes: Optional[str] = None
    lignes: Optional[List[LigneBonCommandeCreate]] = None


class BonCommandeConfirm(BaseModel):
    pass  # Juste pour la confirmation


class BonCommandeResponse(BaseModel):
    id: int
    numero_bc: str
    entreprise_id: int
    fournisseur_id: int
    statut: str
    total_ht: float
    tva: float
    timbre_fiscal: float
    total_ttc: float
    date_creation: datetime
    date_confirmation: Optional[datetime]
    date_livraison_attendue: Optional[date]
    confirmee: bool
    lignes: List[LigneBonCommandeResponse]

    class Config:
        from_attributes = True


# ============ LIGNE RÉCEPTION ============

class LigneReceptionCreate(BaseModel):
    ligne_bc_id: int = Field(..., gt=0)
    quantite_receptionnee: int = Field(..., ge=0)
    quantite_conforme: int = Field(..., ge=0)
    notes_conformite: Optional[str] = None


class LigneReceptionResponse(BaseModel):
    id: int
    ligne_bc_id: int
    quantite_receptionnee: int
    quantite_conforme: int
    quantite_non_conforme: int
    conformite_acceptee: bool
    date_reception: datetime

    class Config:
        from_attributes = True


# ============ RÉCEPTION ============

class ReceptionCreate(BaseModel):
    bon_commande_id: int = Field(..., gt=0)
    numero_bl: Optional[str] = None
    lignes: List[LigneReceptionCreate] = Field(..., min_items=1)
    notes: Optional[str] = None


class ReceptionResponse(BaseModel):
    id: int
    numero_reception: str
    bon_commande_id: int
    entreprise_id: int
    fournisseur_id: int
    statut: str
    date_reception: datetime
    numero_bl: Optional[str]
    lignes: List[LigneReceptionResponse]

    class Config:
        from_attributes = True


# ============ BON DE RETOUR ============

class LigneBonRetourCreate(BaseModel):
    ligne_bc_id: int = Field(..., gt=0)
    quantite_retournee: int = Field(..., gt=0)
    prix_unitaire: float = Field(..., gt=0)


class LigneBonRetourResponse(BaseModel):
    id: int
    ligne_bc_id: int
    quantite_retournee: int
    prix_unitaire: float
    montant_ligne: float

    class Config:
        from_attributes = True


class BonRetourCreate(BaseModel):
    reception_id: int = Field(..., gt=0)
    motif_retour: str
    lignes: List[LigneBonRetourCreate] = Field(..., min_items=1)
    notes: Optional[str] = None


class BonRetourResponse(BaseModel):
    id: int
    numero_br: str
    reception_id: int
    bon_commande_id: int
    entreprise_id: int
    fournisseur_id: int
    statut: str
    total_ht_retour: float
    total_ttc_retour: float
    motif_retour: str
    date_creation: datetime
    lignes: List[LigneBonRetourResponse]

    class Config:
        from_attributes = True


# ============ AVOIR FOURNISSEUR ============

class AvoirFournisseurResponse(BaseModel):
    id: int
    numero_avoir: str
    bon_retour_id: int
    entreprise_id: int
    fournisseur_id: int
    statut: str
    montant_ttc: float
    montant_applique: float
    date_creation: datetime

    class Config:
        from_attributes = True


#  LIGNE FACTURE FOURNISSEUR

class LigneFactureFournisseurCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    designation: str
    quantite_facturee: int = Field(..., gt=0)
    prix_unitaire: float = Field(..., gt=0)


class LigneFactureFournisseurResponse(BaseModel):
    id: int
    product_id: int
    designation: str
    quantite_facturee: int
    prix_unitaire: float
    montant_ligne: float

    class Config:
        from_attributes = True


#  FACTURE FOURNISSEUR 

class FactureFournisseurCreate(BaseModel):
    bon_commande_id: Optional[int] = None
    numero_facture: str
    fournisseur_id: int = Field(..., gt=0)
    entreprise_id: int = Field(..., gt=0)
    date_facture: date
    total_ht: float = Field(..., ge=0)
    total_tva: float = Field(..., ge=0)
    total_ttc: float = Field(..., ge=0)
    date_echeance: Optional[date] = None
    reference_bon_commande_fournisseur: Optional[str] = None
    numero_bon_livraison_fournisseur: Optional[str] = None
    lignes: List[LigneFactureFournisseurCreate] = Field(..., min_items=1)
    notes: Optional[str] = None

    @validator("total_ht", "total_tva", "total_ttc")
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("Les montants ne peuvent pas être négatifs")
        return v


class FactureFournisseurUpdate(BaseModel):
    statut: Optional[str] = None
    notes: Optional[str] = None


class FactureFournisseurResponse(BaseModel):
    id: int
    numero_facture: str
    bon_commande_id: Optional[int]
    entreprise_id: int
    fournisseur_id: int
    statut: str
    total_ht: float
    total_tva: float
    total_ttc: float
    total_ttc_net: float
    date_facture: date
    date_reception: datetime
    date_echeance: Optional[date]
    lignes: List[LigneFactureFournisseurResponse]

    class Config:
        from_attributes = True


# ============ LITIGE FACTURE ============

class LitigeFactureResponse(BaseModel):
    id: int
    facture_id: int
    ecart_quantite: bool
    ecart_prix: bool
    ecart_montant: bool
    details_ecart: str
    seuil_tolerance_depasse: bool
    montant_litige: float
    resolu: bool
    date_detection: datetime

    class Config:
        from_attributes = True


# ============ STATISTIQUES ============

class StatistiquesAchatsResponse(BaseModel):
    total_depenses: float
    total_depenses_payees: float
    nombre_bons_commande: int
    nombre_factures_en_litige: int
    periode: Optional[str] = None