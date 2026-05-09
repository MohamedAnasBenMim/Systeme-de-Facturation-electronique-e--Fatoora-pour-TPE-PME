from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.entreprise import Langue
from app.schemas.comptebancaire_schema import CompteBancaireResponse
from app.schemas.membre_schema import MembreResponse


class EntrepriseCreate(BaseModel):
    nom                 : str
    slogan              : Optional[str]   = None
    forme_juridique     : Optional[str]   = None
    adresse             : str
    ville               : str
    code_postal         : Optional[str]   = None
    pays                : Optional[str]   = "Tunisie"
    telephone           : Optional[str]   = None
    email               : Optional[str]   = None
    site_web            : Optional[str]   = None
    matricule_fiscal    : Optional[str]   = None
    langue              : Optional[Langue] = Langue.FRANCAIS
    couleur_principale  : Optional[str]   = "#1890ff"
    couleur_secondaire  : Optional[str]   = "#f0f0f0"
    pied_de_page        : Optional[str]   = None
    mentions_legales    : Optional[str]   = None
    prefixe_devis       : Optional[str]   = "DEV"
    prefixe_bc          : Optional[str]   = "BC"
    prefixe_bl          : Optional[str]   = "BL"
    prefixe_facture     : Optional[str]   = "FAC"


class EntrepriseUpdate(BaseModel):
    nom                 : Optional[str]    = None
    slogan              : Optional[str]    = None
    forme_juridique     : Optional[str]    = None
    adresse             : Optional[str]    = None
    ville               : Optional[str]    = None
    code_postal         : Optional[str]    = None
    pays                : Optional[str]    = None
    telephone           : Optional[str]    = None
    email               : Optional[str]    = None
    site_web            : Optional[str]    = None
    matricule_fiscal    : Optional[str]    = None
    langue              : Optional[Langue] = None
    couleur_principale  : Optional[str]    = None
    couleur_secondaire  : Optional[str]    = None
    pied_de_page        : Optional[str]    = None
    mentions_legales    : Optional[str]    = None
    prefixe_devis       : Optional[str]    = None
    prefixe_bc          : Optional[str]    = None
    prefixe_bl          : Optional[str]    = None
    prefixe_facture     : Optional[str]    = None


class EntrepriseResponse(BaseModel):
    id                  : int
    nom                 : str
    slogan              : Optional[str]
    logo_url            : Optional[str]
    forme_juridique     : Optional[str]
    adresse             : str
    ville               : str
    code_postal         : Optional[str]
    pays                : str
    telephone           : Optional[str]
    email               : Optional[str]
    site_web            : Optional[str]
    matricule_fiscal    : Optional[str]
    langue              : Langue
    couleur_principale  : str
    couleur_secondaire  : str
    pied_de_page        : Optional[str]
    mentions_legales    : Optional[str]
    prefixe_devis       : str
    prefixe_bc          : str
    prefixe_bl          : str
    prefixe_facture     : str
    owner_id            : int
    est_active          : bool
    date_creation       : datetime
    date_modification   : Optional[datetime]

    class Config:
        from_attributes = True


class EntrepriseConfigResponse(BaseModel):
    id                  : int
    nom                 : str
    slogan              : Optional[str]
    logo_url            : Optional[str]
    adresse             : str
    ville               : str
    pays                : str
    telephone           : Optional[str]
    email               : Optional[str]
    matricule_fiscal    : Optional[str]
    langue              : Langue
    couleur_principale  : str
    couleur_secondaire  : str
    pied_de_page        : Optional[str]
    mentions_legales    : Optional[str]
    prefixe_devis       : str
    prefixe_bc          : str
    prefixe_bl          : str
    prefixe_facture     : str

#Retourne l'entreprise avec toutes ses données liées
class EntrepriseDetailResponse(EntrepriseResponse):
    comptes_bancaires : list[CompteBancaireResponse] = []
    membres           : list[MembreResponse] = []
    #taxes             : list[TaxeResponse] = []

    class Config:
        from_attributes = True