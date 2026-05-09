from sqlalchemy.orm import Session
from app.models.user import User
from app.models.tenant import Tenant
from app.core.password_handler import hash_password

def seed_admin(db: Session):
    existing = db.query(User).filter(User.email == "admin@efatoora.com").first()
    tenant = None
    if existing:
        tenant = db.query(Tenant).filter(Tenant.id == existing.tenant_id).first()
        if tenant is None:
            tenant = Tenant(id=existing.tenant_id)
            db.add(tenant)
            db.commit()
            print("Tenant admin réparé")
        print("Admin existant")
        return

    tenant = Tenant()
    db.add(tenant)
    db.flush()

    admin = User(
        tenant_id=tenant.id,
        email="admin@efatoora.com",
        password=hash_password("Admin@123456"),
        role="ADMIN",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print("   Admin créé : admin@efatoora.com / Admin@123456")
