from sqlalchemy.orm import Session
from app.models.devis import Devis
from app.models.ligne_devis import LigneDevis
from app.schemas.devis_schema import DevisCreate
from app.schemas.ligne_devis_schema import LigneDevisCreate

def valider_lignes(lignes: list[LigneDevisCreate]):
    for ligne in lignes:
        if ligne.quantite <= 0:
            raise ValueError(f"Quantité invalide pour {ligne.produit}")
        if ligne.prix_unitaire <= 0:
            raise ValueError(f"Prix unitaire invalide pour {ligne.produit}")

def calculer_total_ht(lignes: list[LigneDevisCreate]):
    return sum(l.quantite * l.prix_unitaire for l in lignes)


def create_devis(db: Session, devis: DevisCreate):
    valider_lignes(devis.lignes)
    total_ht = calculer_total_ht(devis.lignes)
    tva = total_ht * 0.19  # ou le taux que tu veux
    total_ttc = total_ht + tva
    db_devis = Devis(client=devis.client, total_ht=total_ht)
    db.add(db_devis)
    db.commit()
    db.refresh(db_devis)
    # Ajouter les lignes
    for ligne in devis.lignes:
        db_ligne = LigneDevis(
            produit=ligne.produit,
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