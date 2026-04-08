from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class StatutFacture(str, enum.Enum):
    BROUILLON = "BROUILLON"
    VALIDEE   = "VALIDEE"
    PAYEE     = "PAYEE"
    ANNULEE   = "ANNULEE"

class Facture(Base):
    __tablename__ = "factures"

    id = Column(Integer, primary_key=True, index=True)
    client = Column(String)
    total_ht = Column(Float, default=0)
    tva = Column(Float, default=0)
    total_ttc = Column(Float, default=0)

    lignes = relationship(
    "LigneFacture",
    back_populates="facture",
    cascade="all, delete-orphan")