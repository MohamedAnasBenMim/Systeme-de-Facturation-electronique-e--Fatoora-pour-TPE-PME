from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.db.database import Base


class CompteBancaire(Base):
    __tablename__ = "comptes_bancaires"

    id            = Column(Integer, primary_key=True, index=True)
    entreprise_id = Column(Integer, ForeignKey("entreprises.id", ondelete="CASCADE"), nullable=False)
    banque        = Column(String(255), nullable=False)
    agence        = Column(String(255), nullable=True)
    rib           = Column(String(100), nullable=False)
    iban          = Column(String)   
    swift         = Column(String(50),  nullable=True)
    devise        = Column(String(10),  default="TND")
    date_creation = Column(DateTime,    default=lambda: datetime.now(timezone.utc))

    entreprise = relationship(
        "Entreprise",
        back_populates="comptes_bancaires"
    )