import bcrypt
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from fastapi import Depends, HTTPException, status, Security
import os 

bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

SECRET_KEY = "9f3c2a8d4b6e7f9a1c2d3e4f5a6b7c8d9e0f123456789abcdef123456789abcd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )

def verify_internal_key(api_key: str = Security(api_key_header)):
    if api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API interne invalide"
        )
    return api_key

def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    
        if "sub" not in payload:
            return None

        return payload

    except JWTError:
        return None

def require_admin(payload: dict = Depends(verify_token)):
    if payload.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return payload