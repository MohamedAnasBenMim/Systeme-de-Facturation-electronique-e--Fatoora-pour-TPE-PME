from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt_handler import decode_token
from app.client.user_client import UserClient

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")

    user = UserClient().get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    return user

def require_role(*roles: str):
    def checker(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role") or {}
        role_name = role.get("name") if isinstance(role, dict) else None
        if role_name not in roles:
            raise HTTPException(status_code=403, detail="Accès refusé")
        return current_user
    return checker
