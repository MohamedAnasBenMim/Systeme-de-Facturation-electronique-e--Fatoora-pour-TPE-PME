"""
SEED — Microservice DEPENSE
Exécuter depuis la racine du microservice depense :
    python seeds/seed_depense.py
"""
from app.db.database import SessionLocal, engine, Base
from app.models.depense import Depense, CategorieDepense, StatutDepense
from datetime import date

Base.metadata.create_all(bind=engine)

# product_id correspond au product_id du microservice produit
# None = dépense générale (non liée à un projet)
DEPENSES = [
    # ── Salaires (CHARGE MENSUELLE) ────────────────────────────────────────
    Depense(id=1,  entreprise_id=1, product_id=None, designation="Salaire développeur senior",      categorie=CategorieDepense.SALAIRE,           montant=2800.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,1,31), fournisseur=None,                notes="Janvier 2024"),
    Depense(id=2,  entreprise_id=1, product_id=None, designation="Salaire développeur senior",      categorie=CategorieDepense.SALAIRE,           montant=2800.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,2,29), fournisseur=None,                notes="Février 2024"),
    Depense(id=3,  entreprise_id=1, product_id=None, designation="Salaire développeur senior",      categorie=CategorieDepense.SALAIRE,           montant=2800.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,3,31), fournisseur=None,                notes="Mars 2024"),
    Depense(id=4,  entreprise_id=1, product_id=None, designation="Salaire technicien réseau",       categorie=CategorieDepense.SALAIRE,           montant=1800.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,1,31), fournisseur=None,                notes="Janvier 2024"),
    Depense(id=5,  entreprise_id=1, product_id=None, designation="Salaire technicien réseau",       categorie=CategorieDepense.SALAIRE,           montant=1800.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,2,29), fournisseur=None,                notes="Février 2024"),
    Depense(id=6,  entreprise_id=1, product_id=None, designation="Salaire technicien réseau",       categorie=CategorieDepense.SALAIRE,           montant=1800.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,3,31), fournisseur=None,                notes="Mars 2024"),
    Depense(id=7,  entreprise_id=1, product_id=None, designation="Salaire chargé de formation",     categorie=CategorieDepense.SALAIRE,           montant=1600.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,2,29), fournisseur=None,                notes="Février 2024"),
    Depense(id=8,  entreprise_id=1, product_id=None, designation="Salaire chargé de formation",     categorie=CategorieDepense.SALAIRE,           montant=1600.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,3,31), fournisseur=None,                notes="Mars 2024"),

    # ── Charges fixes ─────────────────────────────────────────────────────
    Depense(id=9,  entreprise_id=1, product_id=None, designation="Loyer bureau Tunis",              categorie=CategorieDepense.CHARGE_FIXE,       montant=1200.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,1,5),  fournisseur="SIMPAR Immobilier",notes="Loyer Jan 2024"),
    Depense(id=10, entreprise_id=1, product_id=None, designation="Loyer bureau Tunis",              categorie=CategorieDepense.CHARGE_FIXE,       montant=1200.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,2,5),  fournisseur="SIMPAR Immobilier",notes="Loyer Fév 2024"),
    Depense(id=11, entreprise_id=1, product_id=None, designation="Loyer bureau Tunis",              categorie=CategorieDepense.CHARGE_FIXE,       montant=1200.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,3,5),  fournisseur="SIMPAR Immobilier",notes="Loyer Mar 2024"),
    Depense(id=12, entreprise_id=1, product_id=None, designation="Abonnement internet fibre 200M",  categorie=CategorieDepense.CHARGE_FIXE,       montant=180.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,1,10), fournisseur="Tunisie Telecom",  notes="Abonnement Jan"),
    Depense(id=13, entreprise_id=1, product_id=None, designation="Abonnement internet fibre 200M",  categorie=CategorieDepense.CHARGE_FIXE,       montant=180.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,2,10), fournisseur="Tunisie Telecom",  notes="Abonnement Fév"),
    Depense(id=14, entreprise_id=1, product_id=None, designation="Abonnement internet fibre 200M",  categorie=CategorieDepense.CHARGE_FIXE,       montant=180.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,3,10), fournisseur="Tunisie Telecom",  notes="Abonnement Mar"),
    Depense(id=15, entreprise_id=1, product_id=None, designation="Assurance multirisque bureau",    categorie=CategorieDepense.CHARGE_FIXE,       montant=320.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,1,15), fournisseur="STAR Assurances",  notes="Assurance annuelle Q1"),
    Depense(id=16, entreprise_id=1, product_id=None, designation="Licences Microsoft 365",          categorie=CategorieDepense.CHARGE_FIXE,       montant=450.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,1,20), fournisseur="Microsoft",        notes="5 licences Business"),

    # ── Achats fournisseurs liés aux projets ──────────────────────────────
    # Projet 1 — Plateforme Web (produit_id=1)
    Depense(id=17, entreprise_id=1, product_id=1,    designation="Hébergement serveur cloud 6 mois",categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=1800.0, statut=StatutDepense.PAYEE,      date_depense=date(2024,1,25), fournisseur="AWS Amazon",       notes="EC2 + RDS pour plateforme STEG"),
    Depense(id=18, entreprise_id=1, product_id=1,    designation="Nom de domaine + certificat SSL", categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=120.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,1,26), fournisseur="GoDaddy",          notes="steg-plateforme.tn"),
    Depense(id=19, entreprise_id=1, product_id=1,    designation="Librairies et licences logiciels",categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=350.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,2,10), fournisseur="JetBrains",        notes="IDE + outils dev"),

    # Projet 2 — Maintenance Réseau (produit_id=2)
    Depense(id=20, entreprise_id=1, product_id=2,    designation="Câbles et connecteurs réseau",    categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=380.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,2,3),  fournisseur="Electrostar",      notes="Consommables maintenance Orange"),
    Depense(id=21, entreprise_id=1, product_id=2,    designation="Logiciel monitoring réseau",      categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=650.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,2,5),  fournisseur="SolarWinds",       notes="Licence annuelle"),

    # Projet 3 — Audit Sécurité (produit_id=3)
    Depense(id=22, entreprise_id=1, product_id=3,    designation="Outil pentest Burp Suite Pro",    categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=520.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,2,8),  fournisseur="PortSwigger",      notes="Licence pour audit TT"),
    Depense(id=23, entreprise_id=1, product_id=3,    designation="Rapport audit sous-traitance",    categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=800.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,2,20), fournisseur="SecureIT Tunisie", notes="Expert externe"),

    # Projet 4 — Formation (produit_id=4)
    Depense(id=24, entreprise_id=1, product_id=4,    designation="Support de cours impression",     categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=180.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,2,15), fournisseur="Imprimerie El Amal",notes="6 classeurs formation"),
    Depense(id=25, entreprise_id=1, product_id=4,    designation="Location salle formation",        categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=450.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,2,18), fournisseur="Hotel Laico Tunis",notes="2 jours × 3 sessions"),

    # ── Coûts projets (heures internes) ──────────────────────────────────
    Depense(id=26, entreprise_id=1, product_id=1,    designation="Heures sup dev plateforme",       categorie=CategorieDepense.COUT_PROJET,       montant=960.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,3,31), fournisseur=None,               notes="32h × 30 DT/h"),
    Depense(id=27, entreprise_id=1, product_id=3,    designation="Heures expert sécurité",          categorie=CategorieDepense.COUT_PROJET,       montant=750.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,3,15), fournisseur=None,               notes="25h × 30 DT/h"),
    Depense(id=28, entreprise_id=1, product_id=2,    designation="Déplacement technicien Orange",   categorie=CategorieDepense.COUT_PROJET,       montant=240.0,  statut=StatutDepense.PAYEE,      date_depense=date(2024,3,20), fournisseur=None,               notes="Frais transport + déj"),

    # ── Dépenses en attente ───────────────────────────────────────────────
    Depense(id=29, entreprise_id=1, product_id=None, designation="Renouvellement domaine .tn",      categorie=CategorieDepense.CHARGE_FIXE,       montant=95.0,   statut=StatutDepense.EN_ATTENTE, date_depense=date(2024,4,30), fournisseur="ATNIC",            notes="Domaine entreprise"),
    Depense(id=30, entreprise_id=1, product_id=1,    designation="Extension stockage serveur",      categorie=CategorieDepense.ACHAT_FOURNISSEUR, montant=320.0,  statut=StatutDepense.EN_ATTENTE, date_depense=date(2024,4,15), fournisseur="AWS Amazon",       notes="Upgrade RDS storage"),
]

def seed():
    db = SessionLocal()
    try:
        if db.query(Depense).count() > 0:
            print("⚠️  Table depenses déjà peuplée — seed ignoré.")
            return
        db.bulk_save_objects(DEPENSES)
        db.commit()
        print(f"✅  {len(DEPENSES)} dépenses insérées.")
    except Exception as e:
        db.rollback()
        print(f"❌  Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
