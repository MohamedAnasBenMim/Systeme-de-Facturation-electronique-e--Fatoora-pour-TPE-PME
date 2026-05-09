from sqlalchemy.orm import Session
from app.models.facture import Facture
from app.models.ligne_facture import LigneFacture


def creer_facture(db: Session, facture_data: dict, lignes):
    try:
        # 1. créer la facture
        db_facture = Facture(
            client=facture_data["client"],
            total_ht=facture_data["total_ht"],
            tva=facture_data["tva"],
            total_ttc=facture_data["total_ttc"]
        )

        db.add(db_facture)
        db.flush()  # récupère ID sans commit

        # 2. ajouter les lignes
        for ligne in lignes:
            db_ligne = LigneFacture(
                facture_id=db_facture.id,
                produit_id=ligne.produit_id,
                quantite=ligne.quantite,
                prix_unitaire=ligne.prix_unitaire
            )
            db.add(db_ligne)

        db.commit()
        db.refresh(db_facture)

        return db_facture

    except Exception as e:
        db.rollback()
        raise e



def get_facture(db: Session, facture_id: int):
    return db.query(Facture).filter(Facture.id == facture_id).first()



def get_factures(db: Session):
    return db.query(Facture).all()


def delete_facture(db: Session, facture_id: int):
    facture = get_facture(db, facture_id)

    if not facture:
        return None

    db.delete(facture)
    db.commit()
    return facture