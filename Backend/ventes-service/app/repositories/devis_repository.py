from sqlalchemy.orm import Session
from app.models.devis import Devis, StatutDevis
from app.models.ligne_devis import LigneDevis
from app.schemas.devis_schema import DevisCreate
from app.schemas.ligne_devis_schema import LigneDevisCreate
from datetime import date
import random

def valider_lignes(lignes: list[LigneDevisCreate]):
    for ligne in lignes:
        if ligne.quantite <= 0:
            raise ValueError(f"Quantité invalide pour {ligne.produit}")
        if ligne.prix_unitaire <= 0:
            raise ValueError(f"Prix unitaire invalide pour {ligne.produit}")

def calculer_total_ht(lignes: list[LigneDevisCreate]):
    return sum(l.quantite * l.prix_unitaire for l in lignes)

def _generer_numero_devis() -> str:
    annee = date.today().year
    random_suffix = random.randint(1000, 9999)
    return f"DEV-{annee}-{random_suffix}"

def create_devis(db: Session, devis: DevisCreate):
    valider_lignes(devis.lignes)
    
    # Calcul des totaux avec remise
    total_ht = calculer_total_ht(devis.lignes)
    taux_remise = getattr(devis, 'taux_remise', 0.0) or 0.0
    montant_remise = round(total_ht * taux_remise / 100, 2)
    total_ht_apres_remise = total_ht - montant_remise
    
    tva = round(total_ht_apres_remise * 0.19, 2)
    total_ttc = round(total_ht_apres_remise + tva, 2)
    
    db_devis = Devis(
        numero_devis=_generer_numero_devis(),
        client_id=devis.client_id,
        date_validite=devis.date_validite,
        statut=devis.statut,
        total_ht=total_ht,
        taux_remise=taux_remise,
        montant_remise=montant_remise,
        tva=tva,
        total_ttc=total_ttc
    )
    db.add(db_devis)
    db.commit()
    db.refresh(db_devis)
    
    # Ajouter les lignes
    for ligne in devis.lignes:
        db_ligne = LigneDevis(
            product_id=ligne.product_id,
            quantite=ligne.quantite,
            prix_unitaire=ligne.prix_unitaire,
            devis_id=db_devis.id
        )
        db.add(db_ligne)
    db.commit()
    db.refresh(db_devis)
    return db_devis


def get_devis(db: Session, devis_id: int) -> Devis | None:
    return db.query(Devis).filter(Devis.id == devis_id).first()

def get_all_devis(db: Session):
    return db.query(Devis).all()

def delete_devis(db: Session, devis_id: int):
    devis = db.query(Devis).filter(Devis.id == devis_id).first()
    if devis:
        db.delete(devis)
        db.commit()
    return devis

def update_statut(db: Session, devis_id: int, nouveau_statut: StatutDevis) -> Devis | None:
    devis = db.query(Devis).filter(Devis.id == devis_id).first()
    if devis:
        devis.statut = nouveau_statut
        db.commit()
        db.refresh(devis)
    return devis

def marquer_converti(db: Session, devis_id: int, type_conversion: str, id_conversion: int) -> Devis | None:
    """Marque le devis comme converti en BC, BL ou Facture"""
    devis = db.query(Devis).filter(Devis.id == devis_id).first()
    if devis:
        if type_conversion == "bc":
            devis.converti_en_bc = id_conversion
        elif type_conversion == "bl":
            devis.converti_en_bl = id_conversion
        elif type_conversion == "facture":
            devis.converti_en_fac = str(id_conversion)
        
        # Marquer le devis comme converti
        if not devis.converti_en_bc and not devis.converti_en_bl:
            devis.statut = StatutDevis.CONVERTI
        
        db.commit()
        db.refresh(devis)
    return devis