from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User
import bcrypt
from passlib.context import CryptContext

DEFAULT_ROLES = [
    {"name": "ADMIN",      "description": "Accès total à toutes les fonctionnalités"},
    {"name": "MANAGER",    "description": "Gestion des utilisateurs et des données"},
    {"name": "ACCOUNTANT", "description": "Accès aux factures et rapports financiers"},
    {"name": "USER",       "description": "Accès en lecture seule"},
]

ADMIN_USER = {
    "username": "admin",
    "email": "admin@efatoora.com",
    "password": "Admin@123456",
    "is_active": True,
}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _hash(password: str) -> str:
    return pwd_context.hash(password)

def seed_roles(db: Session) -> dict:
    """Crée les rôles et retourne un dict name→role"""
    roles = {}
    for r in DEFAULT_ROLES:
        role = db.query(Role).filter(Role.name == r["name"]).first()
        if not role:
            role = Role(**r)
            db.add(role)
            print("  Rôle créé : {r['name']}")
        else:
            print("    Rôle existant : {r['name']}")
        roles[r["name"]] = role
    db.commit()
    return roles

def seed_admin(db: Session, roles: dict) -> None:
    """Crée le compte admin s'il n'existe pas"""
    existing = db.query(User).filter(User.email == ADMIN_USER["email"]).first()
    if existing:
        print("  ⏭  Admin existant : {ADMIN_USER['email']}")
        return

    admin_role = roles.get("ADMIN")
    if not admin_role:
        print("  Rôle ADMIN introuvable, admin non créé")
        return

    admin = User(
        username=ADMIN_USER["username"],
        email=ADMIN_USER["email"],
        password=_hash(ADMIN_USER["password"]),
        is_active=ADMIN_USER["is_active"],
        role_id=admin_role.id,
    )
    db.add(admin)
    db.commit()
    print("   Admin créé : {ADMIN_USER['email']} / {ADMIN_USER['password']}")

def run_seeders(db: Session) -> None:
    print("\ Démarrage des seeders...")
    roles = seed_roles(db)
    seed_admin(db, roles)
    print(" Seeders terminés\n")