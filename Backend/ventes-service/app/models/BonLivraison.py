import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class StatutBonLivraison(str, enum.Enum):
    EN_ATTENTE  = "EN_ATTENTE"
    EN_COURS    = "EN_COURS"
    LIVRE       = "LIVRE"       # livraison complète confirmée
    PARTIEL     = "PARTIEL"     # livraison partielle : un BL restant sera créé
    ANNULE      = "ANNULE"
    FACTURE     = "FACTURE"     # converti en facture


class SourceBonLivraison(str, enum.Enum):
    """Indique depuis quel document le BL a été créé."""
    BON_COMMANDE = "BON_COMMANDE"
    DEVIS        = "DEVIS"
    MANUEL       = "MANUEL"


class BonLivraison(Base):
    __tablename__ = "bons_livraison"

    id              = Column(Integer, primary_key=True, index=True)
    numero          = Column(String(20), unique=True, nullable=False)   # BL-2025-0001

    bc_id           = Column(Integer, ForeignKey("bons_commande.id"), nullable=True)
    devis_id        = Column(Integer, ForeignKey("devis.id"), nullable=True)
    source          = Column(Enum(SourceBonLivraison), nullable=False)

    # Livraison partielle : lien vers le BL parent dont ce BL est le reliquat
    bl_parent_id    = Column(Integer, ForeignKey("bons_livraison.id"), nullable=True)

    client_id       = Column(Integer, nullable=False)
    statut          = Column(Enum(StatutBonLivraison), default=StatutBonLivraison.EN_ATTENTE, nullable=False)
    date_creation   = Column(DateTime, default=datetime.utcnow)
    date_livraison  = Column(DateTime, nullable=True)   # date effective de livraison
    notes           = Column(Text, nullable=True)

    facture_id_externe = Column(Integer, nullable=True)

    montant_ht  = Column(Float, default=0.0)
    montant_tva = Column(Float, default=0.0)
    montant_ttc = Column(Float, default=0.0)

    lignes        = relationship("LigneBonLivraison", back_populates="bon_livraison", cascade="all, delete-orphan")
    bon_commande  = relationship("BonCommande", back_populates="bons_livraison")
    bl_parent     = relationship("BonLivraison", remote_side="BonLivraison.id", foreign_keys=[bl_parent_id])


