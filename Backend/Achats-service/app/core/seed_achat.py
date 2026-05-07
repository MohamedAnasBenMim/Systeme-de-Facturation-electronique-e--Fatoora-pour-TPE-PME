from app.db.database import SessionLocal
from app.models.achat import (
    Fournisseur, BonCommande, LigneBonCommande, Reception, LigneReception,
    StatutBonCommande, StatutReception
)
from datetime import date, datetime, timedelta


def seed():
    db = SessionLocal()
    try:
        if db.query(Fournisseur).count() > 0:
            print("Données d'achats déjà présentes, skipping seed.")
            return

        fournisseurs_data = [
            {
                "nom": "Fournisseur IT Solutions",
                "matricule_fiscal": "1234567890",
                "adresse": "123 Rue de l'Innovation, Tunis",
                "ville": "Tunis",
                "code_postal": "1002",
                "telephone": "+216 71 234 567",
                "email": "contact@it-solutions.tn",
                "contact_principal": "Ahmed Ben Ali",
                "delai_paiement_jours": 30,
                "escompte_pourcent": 2.0,
                "seuil_tolerance_quantite": 5.0,
                "seuil_tolerance_prix": 5.0,
            },
            {
                "nom": "Fournitures Bureau Plus",
                "matricule_fiscal": "0987654321",
                "adresse": "456 Boulevard Industriel, Sfax",
                "ville": "Sfax",
                "code_postal": "3000",
                "telephone": "+216 74 456 789",
                "email": "ventes@fournitures-plus.tn",
                "contact_principal": "Fatima Jendoubi",
                "delai_paiement_jours": 45,
                "escompte_pourcent": 1.5,
                "seuil_tolerance_quantite": 3.0,
                "seuil_tolerance_prix": 2.0,
            }
        ]

        fournisseurs = []
        for f_data in fournisseurs_data:
            fournisseur = Fournisseur(**f_data)
            db.add(fournisseur)
            db.flush()
            fournisseurs.append(fournisseur)

        # Créer quelques bons de commande d'exemple
        bc_data = {
            "numero_bc": "BC-1-000001",
            "entreprise_id": 1,
            "fournisseur_id": fournisseurs[0].id,
            "statut": StatutBonCommande.CONFIRMEE,
            "total_ht": 5000.0,
            "tva": 950.0,
            "timbre_fiscal": 1.0,
            "total_ttc": 5951.0,
            "date_creation": datetime.utcnow(),
            "date_confirmation": datetime.utcnow(),
            "date_livraison_attendue": date.today() + timedelta(days=7),
            "confirmee": True,
            "creer_par_user_id": 1,
            "confirmer_par_user_id": 1,
        }

        bc = BonCommande(**bc_data)
        db.add(bc)
        db.flush()

        # Ajouter des lignes au BC
        lignes_bc = [
            {
                "bon_commande_id": bc.id,
                "product_id": 1,
                "designation": "Ordinateur Portable Dell XPS",
                "reference_fournisseur": "DELL-XPS-15",
                "quantite_commandee": 5,
                "quantite_receptionnable": 5,
                "prix_unitaire": 1000.0,
                "montant_ligne": 5000.0,
            }
        ]

        for l in lignes_bc:
            db.add(LigneBonCommande(**l))

        db.commit()
        print("Seed d'achats terminé avec succès.")

    except Exception as e:
        db.rollback()
        print(f"Erreur lors du seed d'achats: {e}")
    finally:
        db.close()