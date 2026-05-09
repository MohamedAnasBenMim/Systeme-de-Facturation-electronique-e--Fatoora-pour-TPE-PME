from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class LigneFacture(Base):
    __tablename__ = "ligne_factures"

    id             = Column(Integer, primary_key=True, index=True)
    facture_id     = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False)
    product_id     = Column(Integer, nullable=False)
    designation    = Column(String, nullable=False)
    quantite       = Column(Float, nullable=False)
    prix_unitaire  = Column(Float, nullable=False)
    montant_ligne  = Column(Float, nullable=False)

    facture = relationship("Facture", back_populates="lignes")
