# ms-auth/app/services/clerk_service.py
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError
from app.repositories.user_repository import UserRepository
from app.core.jwt_handler import create_access_token, create_refresh_token
from app.models.tenant import Tenant
from app.config import settings
from app.exceptions import AccountDisabledException
import httpx


class ClerkService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.db   = db

    # ──────────────────────────────────────────────
    # 1. Vérifie la signature du webhook Clerk
    # ──────────────────────────────────────────────
    def verify_webhook(self, payload: bytes, headers: dict) -> dict:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        try:
            return wh.verify(payload, headers)
        except WebhookVerificationError:
            raise ValueError("Signature webhook invalide")

    # ──────────────────────────────────────────────
    # 2. Webhook : user.created → provisionne en DB
    # ──────────────────────────────────────────────
    async def handle_user_created(self, clerk_payload: dict) -> None:
        clerk_id = clerk_payload["id"]
        email    = clerk_payload["email_addresses"][0]["email_address"]

        # Idempotence : si déjà créé, on ne fait rien
        if self.repo.get_by_clerk_id(clerk_id):
            return

        # Crée le tenant
        tenant = Tenant()
        self.db.add(tenant)
        self.db.flush()

        # Crée l'utilisateur
        user = self.repo.create_from_clerk(
            email     = email,
            clerk_id  = clerk_id,
            role      = "USER",
            tenant_id = str(tenant.id),
        )

        # Initialise l'entreprise (même logique que register)
        nom_entreprise = clerk_payload.get("first_name", email.split("@")[0])
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{settings.ENTREPRISE_SERVICE_URL}/internal/init",
                    json    = {"nom": nom_entreprise, "email": email},
                    headers = {"X-Tenant-Id": str(tenant.id)},
                    timeout = 5.0,
                )
            except Exception:
                pass  # non bloquant

        self.db.commit()

    # ──────────────────────────────────────────────
    # 3. Échange du token Clerk contre ton JWT interne
    # ──────────────────────────────────────────────
    async def exchange_clerk_token(self, clerk_token: str) -> dict:
        """
        Le frontend envoie son session token Clerk.
        On vérifie avec l'API Clerk, puis on génère
        ton JWT interne habituel.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.clerk.com/v1/sessions/verify",
                headers = {
                    "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                    "Content-Type":  "application/json",
                },
                params  = {"token": clerk_token},
                timeout = 5.0,
            )

        if resp.status_code != 200:
            raise ValueError("Token Clerk invalide ou expiré")

        clerk_data = resp.json()
        clerk_id   = clerk_data["user_id"]

        user = self.repo.get_by_clerk_id(clerk_id)
        if not user:
            raise ValueError("Utilisateur introuvable — webhook non encore reçu")
        if not user.is_active:
            raise AccountDisabledException()

        tenant = self.db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if not tenant or not tenant.is_active:
            raise AccountDisabledException()

        # Récupère entreprise_id (même logique que ton login classique)
        entreprise_id = None
        try:
            r = await httpx.AsyncClient().get(
                f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/by-owner/{user.id}",
                timeout=5.0,
            )
            if r.status_code == 200:
                entreprise_id = r.json().get("id")
        except Exception:
            pass

        payload = {
            "sub":           user.email,
            "user_id":       str(user.id),
            "role":          user.role,
            "tenant_id":     str(user.tenant_id),
            "plan":          tenant.plan,
            "is_active":     tenant.is_active,
            "entreprise_id": entreprise_id,
        }

        return {
            "access_token":  create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "expires_in":    settings.access_token_expire_minutes * 60,
        }