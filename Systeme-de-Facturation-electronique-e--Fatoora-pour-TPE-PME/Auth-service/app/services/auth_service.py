from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RegisterResponse
from app.repositories.user_repository import UserRepository
from app.core.password_handler import verify_password, hash_password
from app.core.jwt_handler import create_access_token, create_refresh_token
from app.exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    AccountDisabledException,
)
from app.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: RegisterRequest) -> RegisterResponse:
        if self.repo.exists_by_email(data.email):
            raise EmailAlreadyExistsException()

        user = self.repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role or "USER",
        )

        return RegisterResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            message="Compte créé avec succès. Veuillez vous connecter.",
        )

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.repo.get_by_email(data.email)

        if not user:
            raise InvalidCredentialsException()
        if not user.is_active:
            raise AccountDisabledException()
        if not verify_password(data.password, user.password):
            raise InvalidCredentialsException()

        payload = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
        }

        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
            expires_in=settings.access_token_expire_minutes * 60,
        )