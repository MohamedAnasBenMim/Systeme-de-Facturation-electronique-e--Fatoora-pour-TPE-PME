import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class StatutBonCommande(str, enum.Enum):
    BROUILLON  = "BROUILLON"
    CONFIRME   = "CONFIRME"
    EN_COURS   = "EN_COURS"       
    LIVRE      = "LIVRE"          
    ANNULE     = "ANNULE"
    FACTURE    = "FACTURE"        


class BonCommande(Base):
    __tablename__ = "bons_commande"

    id              = Column(Integer, primary_key=True, index=True)
    numero          = Column(String(20), unique=True, nullable=False)   # BC-2025-0001
    devis_id        = Column(Integer, ForeignKey("devis.id"), nullable=True)   # null si créé sans devis
    client_id       = Column(Integer, nullable=False)   
    statut          = Column(Enum(StatutBonCommande), default=StatutBonCommande.BROUILLON, nullable=False)
    date_creation   = Column(DateTime, default=datetime.utcnow)
    date_livraison_souhaitee = Column(DateTime, nullable=True)
    notes           = Column(Text, nullable=True)

    montant_ht  = Column(Float, default=0.0)
    montant_tva = Column(Float, default=0.0)
    montant_ttc = Column(Float, default=0.0)

    lignes        = relationship("LigneBonCommande", back_populates="bon_commande", cascade="all, delete-orphan")
    bons_livraison = relationship("BonLivraison", back_populates="bon_commande")


