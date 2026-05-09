import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class StatutDevis(str, enum.Enum):
    BROUILLON = "BROUILLON"
    ENVOYE    = "ENVOYE"
    ACCEPTE   = "ACCEPTE"
    REFUSE    = "REFUSE"
    EXPIRE    = "EXPIRE"
    CONVERTI  = "CONVERTI"   # état terminal : le devis a été converti


class TypeConversionDevis(str, enum.Enum):
    BC      = "BC"
    BL      = "BL"
    FACTURE = "FACTURE"


class Devis(Base):
    __tablename__ = "devis"

    id              = Column(Integer, primary_key=True, index=True)
    numero          = Column(String(20), unique=True, nullable=False)   # DEV-2025-0001
    client_id       = Column(Integer, nullable=False)
    statut          = Column(Enum(StatutDevis), default=StatutDevis.BROUILLON, nullable=False)
    date_creation   = Column(DateTime, default=datetime.utcnow)
    date_expiration = Column(DateTime, nullable=True)
    notes           = Column(Text, nullable=True)

    # Traçabilité conversion
    type_conversion    = Column(Enum(TypeConversionDevis), nullable=True)
    id_document_cible  = Column(Integer, nullable=True)  

    # Remise
    taux_remise    = Column(Float, default=0.0)
    montant_remise = Column(Float, default=0.0)

    # Totaux
    montant_ht  = Column(Float, default=0.0)
    montant_tva = Column(Float, default=0.0)
    montant_ttc = Column(Float, default=0.0)

    # Liens de conversion
    converti_en_bc = Column(Integer, nullable=True)
    converti_en_bl = Column(Integer, nullable=True)

    lignes = relationship("LigneDevis", back_populates="devis", cascade="all, delete-orphan")


