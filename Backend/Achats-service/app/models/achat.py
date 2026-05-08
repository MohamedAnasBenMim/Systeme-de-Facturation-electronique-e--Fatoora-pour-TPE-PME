from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Enum as SAEnum, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import date, datetime
import enum


# ============ ÉNUMÉRATIONS ============

class StatutBonCommande(str, enum.Enum):
    BROUILLON = "BROUILLON"          # Édition en cours
    CONFIRMEE = "CONFIRMEE"          # Immuable, envoyée au fournisseur
    LIVREE = "LIVREE"                # Réceptionnée
    DIFFERENCIEE = "DIFFERENCIEE"    # Écarts de quantité/prix


class StatutReception(str, enum.Enum):
    PARTIELLE = "PARTIELLE"
    COMPLETE = "COMPLETE"
    DIFFERENCIEE = "DIFFERENCIEE"    # Moins que commandé


class StatutBonRetour(str, enum.Enum):
    BROUILLON = "BROUILLON"
    VALIDEE = "VALIDEE"
    TRAITEE = "TRAITEE"              # Avoir généré


class StatutAvoirFournisseur(str, enum.Enum):
    BROUILLON = "BROUILLON"
    VALIDEE = "VALIDEE"
    APPLIQUEE = "APPLIQUEE"          # Créditée sur facture


class StatutFactureFournisseur(str, enum.Enum):
    BROUILLON = "BROUILLON"
    EN_RAPPROCHEMENT = "EN_RAPPROCHEMENT"
    EN_LITIGE = "EN_LITIGE"          # 3-way match failed
    VALIDEE = "VALIDEE"              # Prête pour paiement
    PAYEE = "PAYEE"


#  FOURNISSEUR 

class Fournisseur(Base):
    __tablename__ = "fournisseurs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    nom = Column(String(255), nullable=False)
    matricule_fiscal = Column(String(100), unique=True, nullable=False, index=True)
    
    # Contact
    adresse = Column(String(500), nullable=False)
    ville = Column(String(100), nullable=False)
    code_postal = Column(String(20), nullable=True)
    telephone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    contact_principal = Column(String(255), nullable=True)
    
    # Conditions de paiement
    delai_paiement_jours = Column(Integer, default=30)  # délai de paiement standard
    escompte_pourcent = Column(Float, default=0.0)       # escompte si payé avant délai
    
    # Paramètres de rapprochement
    seuil_tolerance_quantite = Column(Float, default=5.0)  # % toléré
    seuil_tolerance_prix = Column(Float, default=5.0)       # % toléré
    
    # Métadonnées
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    bons_commande = relationship("BonCommande", back_populates="fournisseur", cascade="all, delete-orphan")
    factures = relationship("FactureFournisseur", back_populates="fournisseur", cascade="all, delete-orphan")


# ============ BON DE COMMANDE ============

class BonCommande(Base):
    __tablename__ = "bons_commande"

    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    numero_bc = Column(String(50), unique=True, nullable=False, index=True)
    entreprise_id = Column(Integer, nullable=False)
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"), nullable=False)
    
    # Statut
    statut = Column(SAEnum(StatutBonCommande), default=StatutBonCommande.BROUILLON)
    
    # Montants (calculés automatiquement)
    total_ht = Column(Float, default=0.0)
    tva = Column(Float, default=0.0)
    timbre_fiscal = Column(Float, default=1.0)
    total_ttc = Column(Float, default=0.0)
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_confirmation = Column(DateTime, nullable=True)  # Quand passe en CONFIRMEE (immuable après)
    date_livraison_attendue = Column(Date, nullable=True)
    date_echeance_paiement = Column(Date, nullable=True)
    
    # Immuabilité
    confirmee = Column(Boolean, default=False)  # Flag pour immuabilité
    
    # Traçabilité
    creer_par_user_id = Column(Integer, nullable=True)
    confirmer_par_user_id = Column(Integer, nullable=True)
    
    # Métadonnées
    notes = Column(Text, nullable=True)
    
    # Relations
    fournisseur = relationship("Fournisseur", back_populates="bons_commande")
    lignes = relationship("LigneBonCommande", back_populates="bon_commande", cascade="all, delete-orphan")
    receptions = relationship("Reception", back_populates="bon_commande", cascade="all, delete-orphan")
    factures = relationship("FactureFournisseur", back_populates="bon_commande", cascade="all")
    audit_trail = relationship("AuditTrail", back_populates="bon_commande", cascade="all, delete-orphan")


# ============ LIGNE BON DE COMMANDE ============

class LigneBonCommande(Base):
    __tablename__ = "lignes_bon_commande"

    id = Column(Integer, primary_key=True, index=True)
    
    bon_commande_id = Column(Integer, ForeignKey("bons_commande.id", ondelete="CASCADE"), nullable=False)
    
    # Produit
    product_id = Column(Integer, nullable=False)
    designation = Column(String(500), nullable=False)
    reference_fournisseur = Column(String(100), nullable=True)  # référence catalogue fournisseur
    
    # Quantités et prix
    quantite_commandee = Column(Integer, nullable=False)
    quantite_receptionnable = Column(Integer, nullable=False)  # = quantite_commandee à la création
    quantite_receptionnee = Column(Integer, default=0, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant_ligne = Column(Float, nullable=False)  # quantite * prix_unitaire
    
    # Traçabilité
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    bon_commande = relationship("BonCommande", back_populates="lignes")
    lignes_reception = relationship("LigneReception", back_populates="ligne_bc")
    lignes_facture = relationship("LigneFactureFournisseur", back_populates="ligne_bc")


# ============ RÉCEPTION ============

class Reception(Base):
    __tablename__ = "receptions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    numero_reception = Column(String(50), unique=True, nullable=False, index=True)
    bon_commande_id = Column(Integer, ForeignKey("bons_commande.id"), nullable=False)
    entreprise_id = Column(Integer, nullable=False)
    fournisseur_id = Column(Integer, nullable=False)
    
    # Statut
    statut = Column(SAEnum(StatutReception), default=StatutReception.PARTIELLE)
    
    # Dates
    date_reception = Column(DateTime, default=datetime.utcnow)
    numero_bl = Column(String(50), nullable=True)  # numéro bon de livraison fournisseur
    
    # Traçabilité
    receptionne_par_user_id = Column(Integer, nullable=True)
    
    # Métadonnées
    notes = Column(Text, nullable=True)
    
    # Relations
    bon_commande = relationship("BonCommande", back_populates="receptions")
    lignes = relationship("LigneReception", back_populates="reception", cascade="all, delete-orphan")
    bons_retour = relationship("BonRetour", back_populates="reception", cascade="all, delete-orphan")


# ============ LIGNE RÉCEPTION ============

class LigneReception(Base):
    __tablename__ = "lignes_reception"

    id = Column(Integer, primary_key=True, index=True)
    
    reception_id = Column(Integer, ForeignKey("receptions.id", ondelete="CASCADE"), nullable=False)
    ligne_bc_id = Column(Integer, ForeignKey("lignes_bon_commande.id"), nullable=False)
    
    # Quantités
    quantite_receptionnee = Column(Integer, nullable=False)
    quantite_conforme = Column(Integer, default=0, nullable=False)
    quantite_non_conforme = Column(Integer, default=0, nullable=False)
    
    # Validation
    conformite_acceptee = Column(Boolean, default=False)
    notes_conformite = Column(Text, nullable=True)
    
    # Dates
    date_reception = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    reception = relationship("Reception", back_populates="lignes")
    ligne_bc = relationship("LigneBonCommande", back_populates="lignes_reception")


# ============ BON DE RETOUR ============

class BonRetour(Base):
    __tablename__ = "bons_retour"

    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    numero_br = Column(String(50), unique=True, nullable=False, index=True)
    reception_id = Column(Integer, ForeignKey("receptions.id"), nullable=False)
    bon_commande_id = Column(Integer, ForeignKey("bons_commande.id"), nullable=False)
    entreprise_id = Column(Integer, nullable=False)
    fournisseur_id = Column(Integer, nullable=False)
    
    # Statut
    statut = Column(SAEnum(StatutBonRetour), default=StatutBonRetour.BROUILLON)
    
    # Montants
    total_ht_retour = Column(Float, default=0.0)
    total_ttc_retour = Column(Float, default=0.0)
    
    # Raison du retour
    motif_retour = Column(String(255), nullable=False)  # "Non-conforme", "Défectueux", etc.
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_validation = Column(DateTime, nullable=True)
    
    # Traçabilité
    cree_par_user_id = Column(Integer, nullable=True)
    valide_par_user_id = Column(Integer, nullable=True)
    
    # Métadonnées
    notes = Column(Text, nullable=True)
    
    # Relations
    reception = relationship("Reception", back_populates="bons_retour")
    lignes = relationship("LigneBonRetour", back_populates="bon_retour", cascade="all, delete-orphan")
    avoir = relationship("AvoirFournisseur", uselist=False, back_populates="bon_retour", cascade="all, delete-orphan")


# ============ LIGNE BON DE RETOUR ============

class LigneBonRetour(Base):
    __tablename__ = "lignes_bon_retour"

    id = Column(Integer, primary_key=True, index=True)
    
    bon_retour_id = Column(Integer, ForeignKey("bons_retour.id", ondelete="CASCADE"), nullable=False)
    ligne_bc_id = Column(Integer, ForeignKey("lignes_bon_commande.id"), nullable=False)
    
    # Quantités et prix
    quantite_retournee = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant_ligne = Column(Float, nullable=False)
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    bon_retour = relationship("BonRetour", back_populates="lignes")


# ============ AVOIR FOURNISSEUR ============

class AvoirFournisseur(Base):
    __tablename__ = "avoirs_fournisseur"

    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    numero_avoir = Column(String(50), unique=True, nullable=False, index=True)
    bon_retour_id = Column(Integer, ForeignKey("bons_retour.id"), nullable=False, unique=True)
    entreprise_id = Column(Integer, nullable=False)
    fournisseur_id = Column(Integer, nullable=False)
    
    # Statut
    statut = Column(SAEnum(StatutAvoirFournisseur), default=StatutAvoirFournisseur.BROUILLON)
    
    # Montants (copié du bon retour)
    montant_ht = Column(Float, nullable=False)
    montant_tva = Column(Float, nullable=False)
    montant_ttc = Column(Float, nullable=False)
    
    # Application
    montant_applique = Column(Float, default=0.0)  # Montant utilisé pour créditer une facture
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_validation = Column(DateTime, nullable=True)
    date_application = Column(DateTime, nullable=True)
    
    # Traçabilité
    cree_par_user_id = Column(Integer, nullable=True)
    valide_par_user_id = Column(Integer, nullable=True)
    
    # Relations
    bon_retour = relationship("BonRetour", back_populates="avoir")


# ============ FACTURE FOURNISSEUR ============

class FactureFournisseur(Base):
    __tablename__ = "factures_fournisseur"

    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    numero_facture = Column(String(50), unique=True, nullable=False, index=True)
    bon_commande_id = Column(Integer, ForeignKey("bons_commande.id"), nullable=True)
    entreprise_id = Column(Integer, nullable=False)
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"), nullable=False)
    
    # Statut
    statut = Column(SAEnum(StatutFactureFournisseur), default=StatutFactureFournisseur.BROUILLON)
    
    # Montants
    total_ht = Column(Float, nullable=False)
    total_tva = Column(Float, nullable=False)
    total_ttc = Column(Float, nullable=False)
    
    # Montants ajustés après retours/avoirs
    total_ttc_net = Column(Float, nullable=False)  # = total_ttc - avoirs appliqués
    
    # Dates
    date_facture = Column(Date, nullable=False)
    date_reception = Column(DateTime, default=datetime.utcnow)
    date_echeance = Column(Date, nullable=True)
    
    # Références fournisseur
    reference_bon_commande_fournisseur = Column(String(100), nullable=True)
    numero_bon_livraison_fournisseur = Column(String(100), nullable=True)
    
    # Traçabilité
    saisie_par_user_id = Column(Integer, nullable=True)
    valide_par_user_id = Column(Integer, nullable=True)
    
    # Métadonnées
    notes = Column(Text, nullable=True)
    
    # Relations
    bon_commande = relationship("BonCommande", back_populates="factures")
    fournisseur = relationship("Fournisseur", back_populates="factures")
    lignes = relationship("LigneFactureFournisseur", back_populates="facture", cascade="all, delete-orphan")
    litige = relationship("LitigeFacture", uselist=False, back_populates="facture", cascade="all, delete-orphan")
    audit_trail = relationship("AuditTrail", back_populates="facture_fournisseur", cascade="all, delete-orphan")


# ============ LIGNE FACTURE FOURNISSEUR ============

class LigneFactureFournisseur(Base):
    __tablename__ = "lignes_facture_fournisseur"

    id = Column(Integer, primary_key=True, index=True)
    
    facture_id = Column(Integer, ForeignKey("factures_fournisseur.id", ondelete="CASCADE"), nullable=False)
    ligne_bc_id = Column(Integer, ForeignKey("lignes_bon_commande.id"), nullable=True)
    
    # Produit
    product_id = Column(Integer, nullable=False)
    designation = Column(String(500), nullable=False)
    
    # Quantités et prix
    quantite_facturee = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant_ligne = Column(Float, nullable=False)
    
    # Dates
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    facture = relationship("FactureFournisseur", back_populates="lignes")
    ligne_bc = relationship("LigneBonCommande", back_populates="lignes_facture")


# ============ LITIGE FACTURE (3-WAY MATCH) ============

class LitigeFacture(Base):
    __tablename__ = "litiges_facture"

    id = Column(Integer, primary_key=True, index=True)
    
    facture_id = Column(Integer, ForeignKey("factures_fournisseur.id"), nullable=False, unique=True)
    
    # Type de litige
    ecart_quantite = Column(Boolean, default=False)
    ecart_prix = Column(Boolean, default=False)
    ecart_montant = Column(Boolean, default=False)
    
    # Détails de l'écart
    details_ecart = Column(Text, nullable=False)
    
    # Seuil tolérance
    seuil_tolerance_depasse = Column(Boolean, default=True)
    
    # Montant du litige
    montant_litige = Column(Float, nullable=False)
    
    # Statut du litige
    resolu = Column(Boolean, default=False)
    resolution = Column(Text, nullable=True)
    
    # Dates
    date_detection = Column(DateTime, default=datetime.utcnow)
    date_resolution = Column(DateTime, nullable=True)
    
    # Traçabilité
    detecte_par_user_id = Column(Integer, nullable=True)
    resolu_par_user_id = Column(Integer, nullable=True)
    
    # Relations
    facture = relationship("FactureFournisseur", back_populates="litige")


# ============ AUDIT TRAIL (TRAÇABILITÉ) ============

class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, index=True)
    
    # Références entités
    bon_commande_id = Column(Integer, ForeignKey("bons_commande.id", ondelete="CASCADE"), nullable=True)
    facture_fournisseur_id = Column(Integer, ForeignKey("factures_fournisseur.id", ondelete="CASCADE"), nullable=True)
    
    # Action
    action = Column(String(100), nullable=False)  # "CREATE", "UPDATE", "CONFIRM", "VALIDATE", etc.
    
    # Données modifiées
    ancien_statut = Column(String(50), nullable=True)
    nouveau_statut = Column(String(50), nullable=True)
    details_modification = Column(Text, nullable=True)
    
    # Traçabilité
    user_id = Column(Integer, nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    # Dates
    date_action = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    bon_commande = relationship("BonCommande", back_populates="audit_trail")
    facture_fournisseur = relationship("FactureFournisseur", back_populates="audit_trail")