from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class LigneBonCommande(Base):
    __tablename__ = "lignes_bon_commande"

    id            = Column(Integer, primary_key=True, index=True)
    bc_id         = Column(Integer, ForeignKey("bons_commande.id"), nullable=False)
    devis_ligne_id = Column(Integer, nullable=True)  
    product_id    = Column(Integer, nullable=False)
    description   = Column(String(255), nullable=True)
    quantite      = Column(Float, nullable=False)
    quantite_livree = Column(Float, default=0.0)      
    prix_unitaire = Column(Float, nullable=False)
    taux_tva      = Column(Float, default=20.0)
    montant_ht    = Column(Float, nullable=False)

    bon_commande = relationship("BonCommande", back_populates="lignes")