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

    def create(self, username: str, email: str, hashed_password: str, role_id: int = None) -> User:
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role_id=role_id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user