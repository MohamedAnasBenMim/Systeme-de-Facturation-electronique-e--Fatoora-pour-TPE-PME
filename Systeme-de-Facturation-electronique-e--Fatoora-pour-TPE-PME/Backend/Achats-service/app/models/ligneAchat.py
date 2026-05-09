from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class LigneAchat(Base):
    __tablename__ = "ligne_achats"

    id             = Column(Integer, primary_key=True, index=True)
    achat_id       = Column(Integer, ForeignKey("achats.id", ondelete="CASCADE"), nullable=False)
    product_id     = Column(Integer, nullable=False)
    designation    = Column(String, nullable=False)   
    quantite       = Column(Integer, nullable=False)
    prix_unitaire  = Column(Float, nullable=False)
    montant_ligne  = Column(Float, nullable=False)    

    achat = relationship("Achat", back_populates="lignes")