from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class LigneFacture(Base):
    __tablename__ = "ligne_factures"

    id = Column(Integer, primary_key=True, index=True)
    produit = Column(String)
    quantite = Column(Integer)
    prix_unitaire = Column(Float)

    facture_id = Column(Integer, ForeignKey("factures.id"))

    facture = relationship("Facture", back_populates="lignes")