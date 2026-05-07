# ms-auth/app/services/auth_service.py
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
from app.models.tenant import Tenant
import httpx

class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.db   = db

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        if self.repo.get_by_email(data.email):
            raise EmailAlreadyExistsException(data.email)

        tenant = Tenant()
        self.db.add(tenant)
        self.db.flush()

        user = self.repo.create(
            email           = data.email,
            hashed_password = hash_password(data.password),
            role            = data.role or "USER",
            tenant_id       = str(tenant.id),
        )

        await InternalClient.post(
            settings.ENTREPRISE_SERVICE_URL,
            "/internal/init",
            str(tenant.id),
            {"nom": data.nom_entreprise, "email": data.email}
        )

        self.db.commit()

        return RegisterResponse(
            id        = user.id,
            email     = user.email,
            role      = user.role,
            tenant_id = str(tenant.id),
            message   = "Compte créé avec succès. Veuillez vous connecter.",
        )

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.repo.get_by_email(data.email)
        if not user:
            raise InvalidCredentialsException()
        if not user.is_active:
            raise AccountDisabledException()
        if not verify_password(data.password, user.password):
            raise InvalidCredentialsException()

        tenant = self.db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if not tenant.is_active:
            raise AccountDisabledException()

        # ✅ Récupère entreprise_id depuis le microservice entreprise
        entreprise_id = None
        try:
            r = httpx.get(
                f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/by-owner/{user.id}",
                timeout=5.0
            )
            if r.status_code == 200:
                entreprise_id = r.json().get("id")
        except Exception:
            pass  # pas encore d'entreprise créée
            print(f"[AUTH] ❌ Erreur appel entreprise-service : {e}")

            print(f"[AUTH] Token payload entreprise_id = {entreprise_id}")

        payload = {
            "sub":           user.email,
            "user_id":       str(user.id),
            "role":          user.role,
            "tenant_id":     str(user.tenant_id),
            "plan":          tenant.plan,
            "is_active":     tenant.is_active,
            "entreprise_id": entreprise_id,  # ✅ inclus dans le token
        }

        return TokenResponse(
            access_token  = create_access_token(payload),
            refresh_token = create_refresh_token(payload),
            expires_in    = settings.access_token_expire_minutes * 60,
        )