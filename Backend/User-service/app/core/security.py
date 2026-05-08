from jose import jwt, JWTError
from fastapi.security import HTTPBearer, APIKeyHeader
from fastapi import Depends, HTTPException, status, Security
from passlib.context import CryptContext
import os

bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

# ✅ argon2 (secure + no 72 bytes limit)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ================= PASSWORD =================

def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ================= API KEY =================

def verify_internal_key(api_key: str = Security(api_key_header)):
    if not INTERNAL_API_KEY or api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API interne invalide"
        )
    return api_key

# ================= JWT =================

def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if "sub" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ================= AUTH =================

def require_admin(payload: dict = Depends(verify_token)):
    if payload.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return payload