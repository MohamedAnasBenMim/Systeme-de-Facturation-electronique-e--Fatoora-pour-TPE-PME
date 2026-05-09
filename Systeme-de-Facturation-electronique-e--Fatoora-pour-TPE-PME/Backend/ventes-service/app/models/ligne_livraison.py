from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class LigneBonLivraison(Base):
    __tablename__ = "lignes_bon_livraison"

    id                  = Column(Integer, primary_key=True, index=True)
    bl_id               = Column(Integer, ForeignKey("bons_livraison.id"), nullable=False)
    bc_ligne_id         = Column(Integer, nullable=True)   
    devis_ligne_id      = Column(Integer, nullable=True)   
    product_id          = Column(Integer, nullable=False)
    description         = Column(String(255), nullable=True)
    quantite            = Column(Float, nullable=False)
    quantite_livree     = Column(Float, nullable=False)    
    prix_unitaire       = Column(Float, nullable=False)
    taux_tva            = Column(Float, default=20.0)
    montant_ht          = Column(Float, nullable=False)

    bon_livraison = relationship("BonLivraison", back_populates="lignes")