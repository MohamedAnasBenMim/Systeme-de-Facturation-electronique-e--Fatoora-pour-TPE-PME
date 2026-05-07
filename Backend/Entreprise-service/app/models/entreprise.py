from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base

class Langue(str, enum.Enum):
    FRANCAIS = "fr"
    ARABE    = "ar"

class Entreprise(Base):
    __tablename__ = "entreprises"

    id                  = Column(Integer, primary_key=True, index=True)

    # Profil de base 
    nom                 = Column(String(255), nullable=False)
    slogan              = Column(String(255), nullable=True)
    logo_url            = Column(String(500), nullable=True)
    forme_juridique     = Column(String(100), nullable=True)

    # Coordonnées 
    adresse             = Column(String(500), nullable=False)
    ville               = Column(String(100), nullable=False)
    code_postal         = Column(String(20),  nullable=True)
    pays                = Column(String(100), default="Tunisie")
    telephone           = Column(String(50),  nullable=True)
    email               = Column(String(255), nullable=True)
    site_web            = Column(String(255), nullable=True)

    # Informations fiscales 
    matricule_fiscal    = Column(String(100), nullable=True)

    # Langue
    langue              = Column(Enum(Langue), default=Langue.FRANCAIS)

    # Personnalisation documents
    couleur_principale  = Column(String(20),  default="#1890ff")
    couleur_secondaire  = Column(String(20),  default="#f0f0f0")
    pied_de_page        = Column(Text,        nullable=True)
    mentions_legales    = Column(Text,        nullable=True)

    # Numérotation
    prefixe_devis       = Column(String(20),  default="DEV")
    prefixe_bc          = Column(String(20),  default="BC")
    prefixe_bl          = Column(String(20),  default="BL")
    prefixe_facture     = Column(String(20),  default="FAC")

    # Multi-tenant 
    owner_id            = Column(Integer, nullable=False, unique=True)
    est_active          = Column(Boolean, default=True)
    date_creation       = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    date_modification   = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    comptes_bancaires = relationship(
        "CompteBancaire",
        back_populates   = "entreprise",
        cascade          = "all, delete-orphan",
        lazy             = "select"
    )
    membres          = relationship(
        "MembreEntreprise",
        back_populates   = "entreprise",
        cascade          = "all, delete-orphan",
        lazy             = "select"
    )
    
    cachet = relationship(
        "Cachet",
        back_populates = "entreprise",
        cascade        = "all, delete-orphan",
        uselist        = False,   # one-to-one
        lazy           = "select"
    )

    taxes = relationship(
        "Taxe",
        back_populates = "entreprise",
        cascade        = "all, delete-orphan",
        lazy           = "select"
    )
    groupes_taxes = relationship(
        "GroupeTaxe",
        back_populates = "entreprise",
        cascade        = "all, delete-orphan",
        lazy           = "select"
    )