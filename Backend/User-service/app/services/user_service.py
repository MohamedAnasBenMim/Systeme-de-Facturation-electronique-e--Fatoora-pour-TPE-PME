from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_all(self) -> List[UserResponse]:
        return self.repo.get_all()

    def get_by_id(self, user_id: int) -> UserResponse:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_by_email(self, email: str) -> UserResponse:
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def create(self, data: UserCreate) -> UserResponse:
        if self.repo.get_by_email(data.email):
            raise HTTPException(status_code=409, detail="Email already registered")
        if self.repo.get_by_username(data.username):
            raise HTTPException(status_code=409, detail="Username already taken")
        return self.repo.create(data)

    def update(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = self.get_by_id(user_id)
        if data.email and data.email != user.email:
            if self.repo.get_by_email(data.email):
                raise HTTPException(status_code=409, detail="Email already in use")
        return self.repo.update(user, data)

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        self.repo.delete(user)