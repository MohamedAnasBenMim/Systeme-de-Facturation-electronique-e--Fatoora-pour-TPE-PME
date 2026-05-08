from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, hashed_password: str, tenant_id: str ,role: str) -> User:
        user = User(
            email=email,
            password=hashed_password,
            tenant_id=tenant_id,
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_clerk_id(self, clerk_id: str):
        return self.db.query(User).filter(User.clerk_id == clerk_id).first()

    def create_from_clerk(self, email: str, clerk_id: str, role: str, tenant_id: str):
        user = User(
            email     = email,
            password  = None,          # pas de mot de passe pour OAuth
            clerk_id  = clerk_id,
            role      = role,
            tenant_id = tenant_id,
            is_active = True,
        )
        self.db.add(user)
        self.db.flush()
        return user