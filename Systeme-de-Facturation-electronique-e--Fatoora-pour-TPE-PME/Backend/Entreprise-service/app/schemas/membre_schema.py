from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.membre import PosteEntreprise, StatutMembre
from typing import List, Optional


class PermissionsSchema(BaseModel):
    peut_voir_devis         : bool = True
    peut_creer_devis        : bool = False
    peut_modifier_devis     : bool = False
    peut_supprimer_devis    : bool = False
    peut_voir_factures      : bool = True
    peut_creer_factures     : bool = False
    peut_modifier_factures  : bool = False
    peut_supprimer_factures : bool = False
    peut_voir_clients       : bool = True
    peut_creer_clients      : bool = False
    peut_modifier_clients   : bool = False
    peut_supprimer_clients  : bool = False
    peut_voir_produits      : bool = True
    peut_creer_produits     : bool = False
    peut_modifier_produits  : bool = False
    peut_supprimer_produits : bool = False
    peut_voir_bc            : bool = True
    peut_creer_bc           : bool = False
    peut_voir_bl            : bool = True
    peut_creer_bl           : bool = False
    est_admin               : bool = False


class MembreCreate(BaseModel):
    email       : str
    nom_complet : Optional[str]       = None
    poste       : PosteEntreprise
    #permissions : PermissionsSchema   = PermissionsSchema()
    permissions: Optional[List[str]] = None


class MembreUpdate(BaseModel):
    poste       : Optional[PosteEntreprise]   = None
    statut      : Optional[StatutMembre]      = None
    permissions : Optional[PermissionsSchema] = None


class MembreResponse(BaseModel):
    id              : int
    entreprise_id   : int
    user_id         : Optional[int]
    email           : str
    nom_complet     : Optional[str]
    poste           : PosteEntreprise
    statut          : StatutMembre
    #permissions     : PermissionsSchema
    permissions: Optional[List[str]] = []
    date_invitation : datetime
    date_acceptance : Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_permissions(cls, m) -> "MembreResponse":
        return cls(
            id              = m.id,
            entreprise_id   = m.entreprise_id,
            user_id         = m.user_id,
            email           = m.email,
            nom_complet     = m.nom_complet,
            poste           = m.poste,
            statut          = m.statut,
            date_invitation = m.date_invitation,
            date_acceptance = m.date_acceptance,
            permissions     = PermissionsSchema(
                peut_voir_devis         = m.peut_voir_devis,
                peut_creer_devis        = m.peut_creer_devis,
                peut_modifier_devis     = m.peut_modifier_devis,
                peut_supprimer_devis    = m.peut_supprimer_devis,
                peut_voir_factures      = m.peut_voir_factures,
                peut_creer_factures     = m.peut_creer_factures,
                peut_modifier_factures  = m.peut_modifier_factures,
                peut_supprimer_factures = m.peut_supprimer_factures,
                peut_voir_clients       = m.peut_voir_clients,
                peut_creer_clients      = m.peut_creer_clients,
                peut_modifier_clients   = m.peut_modifier_clients,
                peut_supprimer_clients  = m.peut_supprimer_clients,
                peut_voir_produits      = m.peut_voir_produits,
                peut_creer_produits     = m.peut_creer_produits,
                peut_modifier_produits  = m.peut_modifier_produits,
                peut_supprimer_produits = m.peut_supprimer_produits,
                peut_voir_bc            = m.peut_voir_bc,
                peut_creer_bc           = m.peut_creer_bc,
                peut_voir_bl            = m.peut_voir_bl,
                peut_creer_bl           = m.peut_creer_bl,
                est_admin               = m.est_admin,
            )
        )