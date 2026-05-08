# ms-entreprise/app/models/taxe.py
import uuid
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Table,Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

# Table d'association groupe <-> taxes
groupe_taxe_association = Table(
    "groupe_taxe_items",
    Base.metadata,
    Column("groupe_id", UUID(as_uuid=True), ForeignKey("groupes_taxes.id"), primary_key=True),
    Column("taxe_id",   UUID(as_uuid=True), ForeignKey("taxes.id"),         primary_key=True),
)

class Taxe(Base):
    __tablename__ = "taxes"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entreprise_id = Column(Integer, ForeignKey("entreprises.id"), nullable=False)
    nom           = Column(String(100), nullable=False)       
    code          = Column(String(20),  nullable=False)       
    taux          = Column(Float,       nullable=False)       # ex: 19.0
    description   = Column(String(255), nullable=True)
    est_active    = Column(Boolean, default=True)
    est_defaut    = Column(Boolean, default=False)            # appliquée automatiquement

    groupes = relationship("GroupeTaxe", secondary=groupe_taxe_association, back_populates="taxes")

    entreprise = relationship("Entreprise", back_populates="taxes")



class GroupeTaxe(Base):
    __tablename__ = "groupes_taxes"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entreprise_id = Column(Integer, ForeignKey("entreprises.id"), nullable=False)
    nom           = Column(String(100), nullable=False)       # ex: "TVA + FODEC"
    description   = Column(String(255), nullable=True)
    est_actif     = Column(Boolean, default=True)

    taxes = relationship("Taxe", secondary=groupe_taxe_association, back_populates="groupes")

    entreprise = relationship("Entreprise", back_populates="groupes_taxes")
