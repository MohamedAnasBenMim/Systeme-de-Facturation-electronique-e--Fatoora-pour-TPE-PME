from sqlalchemy import Column, Integer, Float, String, Date, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import date
import enum


class StatutFacture(str, enum.Enum):
    BROUILLON = "BROUILLON"
    VALIDEE   = "VALIDEE"
    PAYEE     = "PAYEE"


class Facture(Base):
    __tablename__ = "factures"

    id              = Column(Integer, primary_key=True, index=True)

    client_id       = Column(Integer, nullable=False)          
    entreprise_id   = Column(Integer, nullable=False)    
    numero          = Column(String, unique=True, nullable=False)      

    total_ht        = Column(Float, default=0.0)
    tva             = Column(Float, default=0.0)               
    timbre_fiscal   = Column(Float, default=1.0)               
    total_ttc       = Column(Float, default=0.0)

    
    date_creation   = Column(Date, default=date.today)
    date_echeance   = Column(Date, nullable=True)

    #traçabilité des factures 
    source          = Column(String, nullable=True)   # DEVIS", BL
    source_id       = Column(Integer, nullable=True)  # le document sorce

    
    statut          = Column(SAEnum(StatutFacture), default=StatutFacture.BROUILLON)

    
    pdf_path        = Column(String, nullable=True)

   
    lignes = relationship(
        "LigneFacture",
        back_populates="facture",
        cascade="all, delete-orphan"
    )