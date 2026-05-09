from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
from datetime import datetime, timedelta


def create_access_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    # payload DOIT contenir tenant_id, role, plan
    # votre code existant fonctionne — assurez-vous juste que
    # le payload passé contient ces clés
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
    except JWTError:
        return None