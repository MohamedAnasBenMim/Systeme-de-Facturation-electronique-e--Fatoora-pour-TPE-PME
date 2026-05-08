from sqlalchemy import Column, Integer, Float, Date, Enum, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum
from datetime import date

class StatutDevis(str, enum.Enum):
    EN_ATTENTE = "EN_ATTENTE"
    BROUILLON = "BROUILLON"
    REFUSE = "REFUSE"
    EXPIRE = "EXPIRE"

class Devis(Base):
    __tablename__ = "devis"

    id = Column(Integer, primary_key=True, index=True)
    client = Column(String, nullable=False)
    date_creation = Column(Date, default=date.today)
    date_validite = Column(Date, nullable=True)
    statut = Column(Enum(StatutDevis), default=StatutDevis.BROUILLON)
    total_ht = Column(Float, default=0)
    tva = Column(Float, default=0)
    total_ttc = Column(Float, default=0)
    lignes = relationship(
        "LigneDevis",
        back_populates="devis",
        cascade="all, delete-orphan",
        lazy="selectin"
    )