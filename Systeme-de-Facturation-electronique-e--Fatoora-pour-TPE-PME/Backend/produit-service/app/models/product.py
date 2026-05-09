import enum
from sqlalchemy import (
    Column, String, Float, Boolean, Integer,
    ForeignKey, Text, Enum, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class TypeArticle(str, enum.Enum):
    PRODUIT = "PRODUIT"
    SERVICE = "SERVICE"


class Categorie(Base):
    __tablename__ = "categories"

    id            = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    entreprise_id = Column(Integer, nullable=False, index=True)
    nom           = Column(String(100), nullable=False)
    description   = Column(String(255), nullable=True)
    parent_id     = Column(Integer, ForeignKey("categories.id"), nullable=True)  # ✅

    parent       = relationship("Categorie", remote_side="Categorie.id", backref="sous_categories")
    produits     = relationship("Produit", back_populates="categorie")



class UniteMesure(Base):
    __tablename__ = "unites_mesure"

    id            = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    entreprise_id = Column(Integer, nullable=False, index=True)
    nom           = Column(String(50), nullable=False)
    code          = Column(String(20), nullable=False)

    produits      = relationship("Produit", back_populates="unite")


class Produit(Base):
    __tablename__ = "produits"

    id            = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    entreprise_id = Column(Integer, nullable=False, index=True)

    # ── Identification ──────────────────────────────────
    type          = Column(Enum(TypeArticle), nullable=False, default=TypeArticle.PRODUIT)
    designation   = Column(String(255), nullable=False)
    reference     = Column(String(100), nullable=True)
    code_barre    = Column(String(100), nullable=True)
    description   = Column(Text,        nullable=True)
    image_url     = Column(String(500), nullable=True)
    marque        = Column(String(100), nullable=True)

    # ── Classification ──────────────────────────────────
    categorie_id  = Column(Integer, ForeignKey("categories.id"), nullable=True)      # ✅
    unite_id      = Column(Integer, ForeignKey("unites_mesure.id"), nullable=True)   # ✅

    # ── Prix ────────────────────────────────────────────
    prix_achat_ht  = Column(Float, default=0.0)
    prix_vente_ht  = Column(Float, nullable=False, default=0.0)
    prix_vente_ttc = Column(Float, nullable=True)


    taxe_id        = Column(String(36), nullable=True)   
    groupe_taxe_id = Column(String(36), nullable=True)   

    # ── Stock ───────────────────────────────────────────
    is_stockable   = Column(Boolean, default=True)

    # ── Statut ──────────────────────────────────────────
    est_actif          = Column(Boolean, default=True)
    date_creation      = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    date_modification  = Column(DateTime, nullable=True,
                                onupdate=lambda: datetime.now(timezone.utc))

    categorie = relationship("Categorie", back_populates="produits")
    unite     = relationship("UniteMesure", back_populates="produits")

    __table_args__ = (
        UniqueConstraint("entreprise_id", "reference", name="uq_produit_ref"),
    )