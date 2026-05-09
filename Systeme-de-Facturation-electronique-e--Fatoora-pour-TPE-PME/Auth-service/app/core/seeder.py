from sqlalchemy.orm import Session
from app.models.user import User
from app.core.password_handler import hash_password

def seed_admin(db: Session):
    existing = db.query(User).filter(User.email == "admin@efatoora.com").first()
    if existing:
        print("  ⏭️  Admin existant")
        return

    admin = User(
        email="admin@efatoora.com",
        password=hash_password("Admin@123456"),
        role="ADMIN",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print("   Admin créé : admin@efatoora.com / Admin@123456")