"""
SEED — Microservice FACTURE
Exécuter depuis la racine du microservice facture :
    python seeds/seed_facture.py
"""
from app.db.database import SessionLocal, engine, Base
from app.models.facture import Facture, StatutFacture
from app.models.ligneFacture import LigneFacture
from datetime import date
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    try:
        if db.query(Facture).count() > 0:
            print("⚠️  Table factures déjà peuplée — seed ignoré.")
            return

        factures_list = [
            # CLIENT 1 — STEG Tunisie
            Facture(id=1,  client_id=1, entreprise_id=1, total_ht=16000.0, tva=3040.0, timbre_fiscal=1.0, total_ttc=19041.0, date_creation=date(2024,1,20), date_echeance=date(2024,2,20), statut=StatutFacture.PAYEE),
            Facture(id=2,  client_id=1, entreprise_id=1, total_ht=5600.0,  tva=1064.0, timbre_fiscal=1.0, total_ttc=6665.0,  date_creation=date(2024,3,10), date_echeance=date(2024,4,10), statut=StatutFacture.PAYEE),
            Facture(id=3,  client_id=1, entreprise_id=1, total_ht=2800.0,  tva=532.0,  timbre_fiscal=1.0, total_ttc=3333.0,  date_creation=date(2024,4,5),  date_echeance=date(2024,5,5),  statut=StatutFacture.PAYEE),
            Facture(id=4,  client_id=1, entreprise_id=1, total_ht=4200.0,  tva=798.0,  timbre_fiscal=1.0, total_ttc=4999.0,  date_creation=date(2024,5,1),  date_echeance=date(2024,6,1),  statut=StatutFacture.VALIDEE),
            # CLIENT 2 — Orange Tunisie
            Facture(id=5,  client_id=2, entreprise_id=1, total_ht=4500.0,  tva=855.0,  timbre_fiscal=1.0, total_ttc=5356.0,  date_creation=date(2024,2,1),  date_echeance=date(2024,3,1),  statut=StatutFacture.PAYEE),
            Facture(id=6,  client_id=2, entreprise_id=1, total_ht=4500.0,  tva=855.0,  timbre_fiscal=1.0, total_ttc=5356.0,  date_creation=date(2024,3,1),  date_echeance=date(2024,4,1),  statut=StatutFacture.PAYEE),
            Facture(id=7,  client_id=2, entreprise_id=1, total_ht=3600.0,  tva=684.0,  timbre_fiscal=1.0, total_ttc=4285.0,  date_creation=date(2024,4,1),  date_echeance=date(2024,5,1),  statut=StatutFacture.VALIDEE),
            # CLIENT 3 — Tunisie Telecom
            Facture(id=8,  client_id=3, entreprise_id=1, total_ht=8400.0,  tva=1596.0, timbre_fiscal=1.0, total_ttc=9997.0,  date_creation=date(2024,2,15), date_echeance=date(2024,3,15), statut=StatutFacture.PAYEE),
            Facture(id=9,  client_id=3, entreprise_id=1, total_ht=1200.0,  tva=228.0,  timbre_fiscal=1.0, total_ttc=1429.0,  date_creation=date(2024,4,15), date_echeance=date(2024,5,15), statut=StatutFacture.VALIDEE),
            # CLIENT 4 — Amen Bank
            Facture(id=10, client_id=4, entreprise_id=1, total_ht=2700.0,  tva=513.0,  timbre_fiscal=1.0, total_ttc=3214.0,  date_creation=date(2024,2,20), date_echeance=date(2024,3,20), statut=StatutFacture.PAYEE),
            Facture(id=11, client_id=4, entreprise_id=1, total_ht=2700.0,  tva=513.0,  timbre_fiscal=1.0, total_ttc=3214.0,  date_creation=date(2024,3,20), date_echeance=date(2024,4,20), statut=StatutFacture.PAYEE),
            Facture(id=12, client_id=4, entreprise_id=1, total_ht=1800.0,  tva=342.0,  timbre_fiscal=1.0, total_ttc=2143.0,  date_creation=date(2024,4,20), date_echeance=date(2024,5,20), statut=StatutFacture.BROUILLON),
            # CLIENT 5 — BH Bank
            Facture(id=13, client_id=5, entreprise_id=1, total_ht=1800.0,  tva=342.0,  timbre_fiscal=1.0, total_ttc=2143.0,  date_creation=date(2024,3,15), date_echeance=date(2024,4,15), statut=StatutFacture.PAYEE),
            Facture(id=14, client_id=5, entreprise_id=1, total_ht=1800.0,  tva=342.0,  timbre_fiscal=1.0, total_ttc=2143.0,  date_creation=date(2024,4,15), date_echeance=date(2024,5,15), statut=StatutFacture.VALIDEE),
            # CLIENT 6 — Attijari Bank
            Facture(id=15, client_id=6, entreprise_id=1, total_ht=2400.0,  tva=456.0,  timbre_fiscal=1.0, total_ttc=2857.0,  date_creation=date(2024,4,10), date_echeance=date(2024,5,10), statut=StatutFacture.VALIDEE),
        ]

        # ✅ FIX 1 : variable nommée lignes_list
        lignes_list = [
            LigneFacture(facture_id=1,  product_id=1,  designation="Développement Plateforme Web",       quantite=2, prix_unitaire=8000.0, montant_ligne=16000.0),
            LigneFacture(facture_id=2,  product_id=5,  designation="Ordinateur Portable Dell Latitude",  quantite=2, prix_unitaire=2800.0, montant_ligne=5600.0),
            LigneFacture(facture_id=3,  product_id=6,  designation="Switch Cisco 24 ports",              quantite=2, prix_unitaire=1200.0, montant_ligne=2400.0),
            LigneFacture(facture_id=3,  product_id=8,  designation="Câble RJ45 Cat6 (boîte 100m)",       quantite=4, prix_unitaire=85.0,   montant_ligne=340.0),
            LigneFacture(facture_id=3,  product_id=9,  designation="Onduleur APC 1500VA",                quantite=1, prix_unitaire=420.0,  montant_ligne=420.0),
            LigneFacture(facture_id=4,  product_id=2,  designation="Maintenance Réseau & Infrastructure", quantite=3, prix_unitaire=1400.0, montant_ligne=4200.0),
            LigneFacture(facture_id=5,  product_id=2,  designation="Maintenance Réseau & Infrastructure", quantite=3, prix_unitaire=1500.0, montant_ligne=4500.0),
            LigneFacture(facture_id=6,  product_id=2,  designation="Maintenance Réseau & Infrastructure", quantite=3, prix_unitaire=1500.0, montant_ligne=4500.0),
            LigneFacture(facture_id=7,  product_id=2,  designation="Maintenance Réseau & Infrastructure", quantite=4, prix_unitaire=900.0,  montant_ligne=3600.0),
            LigneFacture(facture_id=8,  product_id=3,  designation="Audit Sécurité Informatique",        quantite=2, prix_unitaire=4200.0, montant_ligne=8400.0),
            LigneFacture(facture_id=9,  product_id=10, designation="Cartouche Toner HP 26A",             quantite=8, prix_unitaire=95.0,   montant_ligne=760.0),
            LigneFacture(facture_id=9,  product_id=7,  designation="Imprimante HP LaserJet Pro",          quantite=1, prix_unitaire=650.0,  montant_ligne=650.0),
            LigneFacture(facture_id=10, product_id=4,  designation="Formation & Consulting IT",           quantite=3, prix_unitaire=900.0,  montant_ligne=2700.0),
            LigneFacture(facture_id=11, product_id=4,  designation="Formation & Consulting IT",           quantite=3, prix_unitaire=900.0,  montant_ligne=2700.0),
            LigneFacture(facture_id=12, product_id=4,  designation="Formation & Consulting IT",           quantite=2, prix_unitaire=900.0,  montant_ligne=1800.0),
            LigneFacture(facture_id=13, product_id=2,  designation="Maintenance Réseau & Infrastructure", quantite=2, prix_unitaire=900.0,  montant_ligne=1800.0),
            LigneFacture(facture_id=14, product_id=2,  designation="Maintenance Réseau & Infrastructure", quantite=2, prix_unitaire=900.0,  montant_ligne=1800.0),
            LigneFacture(facture_id=15, product_id=1,  designation="Développement Plateforme Web",        quantite=1, prix_unitaire=2400.0, montant_ligne=2400.0),
        ]

        db.bulk_save_objects(factures_list)
        db.flush()
        db.bulk_save_objects(lignes_list)
        db.commit()

        db.execute(text("SELECT setval('factures_id_seq', (SELECT MAX(id) FROM factures))"))
        db.execute(text("SELECT setval('lignefactures_id_seq', (SELECT MAX(id) FROM ligne_factures))"))
        db.commit()

        print(f"✅  {len(factures_list)} factures + {len(lignes_list)} lignes insérées.")

    except Exception as e:
        db.rollback()
        print(f"❌  Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()