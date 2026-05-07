"""
SEED — Microservice CLIENT
Exécuter depuis la racine du microservice client :
    python seeds/seed_client.py
"""
from app.db.database import SessionLocal, engine, Base
from app.models.client import Client

Base.metadata.create_all(bind=engine)

CLIENTS = [
    Client( nom="Ben Ali",     prenom="Mehdi",   email="mehdi.benali@steg.tn",       telephone="71 123 456", adresse="Rue de l'Energie, Tunis",          matricule_fiscal="1234567A/P/M000"),
    Client( nom="Trabelsi",    prenom="Sonia",   email="s.trabelsi@orange.tn",        telephone="71 234 567", adresse="Avenue Habib Bourguiba, Tunis",     matricule_fiscal="2345678B/P/M000"),
    Client( nom="Chaabane",    prenom="Karim",   email="k.chaabane@tunisietelecom.tn",telephone="71 345 678", adresse="Avenue de Carthage, Tunis",         matricule_fiscal="3456789C/P/M000"),
    Client( nom="Hamrouni",    prenom="Leila",   email="l.hamrouni@amenbank.com.tn",  telephone="71 456 789", adresse="Rue Hédi Nouira, Tunis",            matricule_fiscal="4567890D/P/M000"),
    Client( nom="Monastiri",   prenom="Yassine", email="y.monastiri@bhbank.tn",       telephone="71 567 890", adresse="Avenue Mohamed V, Tunis",           matricule_fiscal="5678901E/P/M000"),
    Client( nom="Jebali",      prenom="Ines",    email="i.jebali@attijari.tn",        telephone="71 678 901", adresse="Rue Jamel Abdennasser, Sfax",       matricule_fiscal="6789012F/P/M000"),
    Client( nom="Boughanmi",   prenom="Rami",    email="r.boughanmi@topnet.tn",       telephone="71 789 012", adresse="Rue Ibn Khaldoun, Sousse",          matricule_fiscal="7890123G/P/M000"),
    Client( nom="Essid",       prenom="Amira",   email="a.essid@hexabyte.tn",         telephone="71 890 123", adresse="Avenue de la République, Monastir", matricule_fiscal="8901234H/P/M000"),
]

def seed():
    db = SessionLocal()
    try:
        if db.query(Client).count() > 0:
            print("⚠️  Table clients déjà peuplée — seed ignoré.")
            return
        db.bulk_save_objects(CLIENTS)
        db.commit()
        print(f"✅  {len(CLIENTS)} clients insérés.")
    except Exception as e:
        db.rollback()
        print(f"❌  Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
