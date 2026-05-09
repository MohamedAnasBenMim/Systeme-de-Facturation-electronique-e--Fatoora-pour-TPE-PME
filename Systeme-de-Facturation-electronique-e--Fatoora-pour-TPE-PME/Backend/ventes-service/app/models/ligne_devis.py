from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class LigneDevis(Base):
    __tablename__ = "lignes_devis"

    id          = Column(Integer, primary_key=True, index=True)
    devis_id    = Column(Integer, ForeignKey("devis.id"), nullable=False)
    product_id  = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)
    quantite    = Column(Float, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant_tva    = Column(Float, default=20.0)
    montant_ht  = Column(Float, nullable=False)

    devis = relationship("Devis", back_populates="lignes")

  