# app/models/membre.py
from sqlalchemy import (
    Column, Integer, String,
    Boolean, ForeignKey, DateTime, Enum
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base



class PosteEntreprise(str, enum.Enum):
    PROPRIETAIRE = "PROPRIETAIRE"
    DIRECTEUR    = "DIRECTEUR"
    COMPTABLE    = "COMPTABLE"
    COMMERCIAL   = "COMMERCIAL"
    MAGASINIER   = "MAGASINIER"
    SECRETAIRE   = "SECRETAIRE"
    AUTRE        = "AUTRE"


class StatutMembre(str, enum.Enum):
    ACTIF      = "ACTIF"
    INACTIF    = "INACTIF"
    EN_ATTENTE = "EN_ATTENTE"


class MembreEntreprise(Base):
    __tablename__ = "membres_entreprise"

    id            = Column(Integer, primary_key=True, index=True)
    entreprise_id = Column(
        Integer,
        ForeignKey("entreprises.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Référence User
    user_id     = Column(Integer,     nullable=True)
    email       = Column(String(255), nullable=False)
    nom_complet = Column(String(255), nullable=True)

    # Rôle
    poste  = Column(Enum(PosteEntreprise), nullable=False)
    statut = Column(Enum(StatutMembre), default=StatutMembre.EN_ATTENTE)

    # Permissions Devis
    peut_voir_devis      = Column(Boolean, default=True)
    peut_creer_devis     = Column(Boolean, default=False)
    peut_modifier_devis  = Column(Boolean, default=False)
    peut_supprimer_devis = Column(Boolean, default=False)

    # Permissions Factures
    peut_voir_factures      = Column(Boolean, default=True)
    peut_creer_factures     = Column(Boolean, default=False)
    peut_modifier_factures  = Column(Boolean, default=False)
    peut_supprimer_factures = Column(Boolean, default=False)

    # Permissions Clients
    peut_voir_clients      = Column(Boolean, default=True)
    peut_creer_clients     = Column(Boolean, default=False)
    peut_modifier_clients  = Column(Boolean, default=False)
    peut_supprimer_clients = Column(Boolean, default=False)

    # Permissions Produits
    peut_voir_produits      = Column(Boolean, default=True)
    peut_creer_produits     = Column(Boolean, default=False)
    peut_modifier_produits  = Column(Boolean, default=False)
    peut_supprimer_produits = Column(Boolean, default=False)

    # Permissions BC
    peut_voir_bc  = Column(Boolean, default=True)
    peut_creer_bc = Column(Boolean, default=False)

    # Permissions BL
    peut_voir_bl  = Column(Boolean, default=True)
    peut_creer_bl = Column(Boolean, default=False)

    # Admin
    est_admin = Column(Boolean, default=False)

    # Dates
    date_invitation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    date_acceptance = Column(DateTime, nullable=True)

    # Relation
    entreprise = relationship(
        "Entreprise",
        back_populates="membres"
    )