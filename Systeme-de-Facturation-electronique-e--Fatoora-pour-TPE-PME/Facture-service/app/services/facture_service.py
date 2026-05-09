from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.models.facture import Facture
from app.models.ligneFacture import LigneFacture
from app.schemas.ligne_facture_schema import LigneFactureCreate



def valider_lignes(lignes: List[LigneFactureCreate]):
    for ligne in lignes:
        if ligne.quantite <= 0:
            raise ValueError(f"Quantité invalide pour le produit {ligne.produit}")
        if ligne.prix_unitaire <= 0:
            raise ValueError(f"Prix unitaire invalide pour le produit {ligne.produit}")

def calculer_totaux(lignes: List[LigneFactureCreate]):
    total_ht = sum(ligne.quantite * ligne.prix_unitaire for ligne in lignes)
    tva = total_ht * 0.19  # TVA 19%
    total_ttc = total_ht + tva
    return total_ht, tva, total_ttc

def preparer_facture(client: str, lignes: List[LigneFactureCreate]):
    valider_lignes(lignes)
    total_ht, tva, total_ttc = calculer_totaux(lignes)
    return {"client": client, "total_ht": total_ht, "tva": tva, "total_ttc": total_ttc}


# Fonctions CRUD facture


def create_facture(db: Session, client: str, lignes: List[LigneFactureCreate]):
    data = preparer_facture(client, lignes)
    try:
        with db.begin():  # transaction atomique
            facture = Facture(
                client=data["client"],
                total_ht=data["total_ht"],
                tva=data["tva"],
                total_ttc=data["total_ttc"]
            )
            db.add(facture)
            db.flush()  # récupère l'ID de la facture

            for ligne in lignes:
                db.add(LigneFacture(
                    facture_id=facture.id,
                    produit=ligne.produit,
                    quantite=ligne.quantite,
                    prix_unitaire=ligne.prix_unitaire
                ))
            db.refresh(facture)
            return facture
    except SQLAlchemyError as e:
        raise e

def get_all_factures(db: Session):
    return db.query(Facture).all()

def get_facture(db: Session, facture_id: int):
    return db.query(Facture).filter(Facture.id == facture_id).first()

def update_facture(db: Session, facture_id: int, client: str = None, lignes: List[LigneFactureCreate] = None):
    facture = get_facture(db, facture_id)
    if not facture:
        return None
    try:
        with db.begin():
            if client:
                facture.client = client

            if lignes is not None:
                # supprimer anciennes lignes
                for ligne in facture.lignes:
                    db.delete(ligne)

                data = preparer_facture(facture.client, lignes)
                facture.total_ht = data["total_ht"]
                facture.tva = data["tva"]
                facture.total_ttc = data["total_ttc"]

                for ligne in lignes:
                    db.add(LigneFacture(
                        facture_id=facture.id,
                        produit=ligne.produit,
                        quantite=ligne.quantite,
                        prix_unitaire=ligne.prix_unitaire
                    ))

            db.refresh(facture)
            return facture
    except SQLAlchemyError as e:
        raise e

def delete_facture(db: Session, facture_id: int):
    facture = get_facture(db, facture_id)
    if not facture:
        raise Exception("Not found")
  
    db.delete(facture)
    db.commit()
    return {
    "id": facture_id,
    "status": "deleted"
    }
   