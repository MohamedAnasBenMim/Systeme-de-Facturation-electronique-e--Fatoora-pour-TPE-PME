# app/models/depense.py
from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey,Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import date
import enum

class CategorieDepense(str, enum.Enum):
    ACHAT_FOURNISSEUR  = "ACHAT_FOURNISSEUR"   # matériel, stock
    SALAIRE            = "SALAIRE"              # ressources humaines
    CHARGE_FIXE        = "CHARGE_FIXE"          # loyer, abonnements
    COUT_PROJET        = "COUT_PROJET"          # heures travaillées sur un projet/service
    AUTRE              = "AUTRE"

class StatutDepense(str, enum.Enum):
    EN_ATTENTE  = "EN_ATTENTE"
    PAYEE       = "PAYEE"
    ANNULEE     = "ANNULEE"

class Depense(Base):
    __tablename__ = "depenses"

    id              = Column(Integer, primary_key=True, index=True)
    entreprise_id   = Column(Integer, nullable=False)       # lien microservice entreprise

    # Lien optionnel vers un projet/service (product_id du microservice produit)
    # Si NULL = dépense générale, si renseigné = dépense liée à un projet
    product_id       = Column(Integer, nullable=True)

    designation     = Column(String, nullable=False)        # description de la dépense
    categorie       = Column(Enum(CategorieDepense), nullable=False)
    montant         = Column(Float, nullable=False)
    statut          = Column(SAEnum(StatutDepense) , default=StatutDepense.EN_ATTENTE)

    date_depense    = Column(Date, default=date.today)
    fournisseur     = Column(String, nullable=True)         # nom fournisseur si achat
    notes           = Column(String, nullable=True)