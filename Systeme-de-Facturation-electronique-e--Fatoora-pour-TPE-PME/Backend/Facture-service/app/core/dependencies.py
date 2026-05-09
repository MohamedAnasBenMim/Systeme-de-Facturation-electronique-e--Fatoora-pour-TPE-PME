from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
   
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant — ajoutez : Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: int = payload.get("user_id")
        email: str   = payload.get("sub")
        role: str    = payload.get("role")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide — données manquantes",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"user_id": user_id, "email": email, "role": role}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )



def require_role(*roles: str):
    """
    Vérifie que l'utilisateur connecté possède l'un des rôles requis.

    Exemple :
        @router.delete("/{id}", dependencies=[Depends(require_role("ROLE_ADMIN"))])
    """
    def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé — rôle(s) requis : {', '.join(roles)}",
            )
        return current_user
    return checker


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict | None:
    """
    Retourne l'utilisateur si un token valide est fourni, sinon None.
    Utile pour les routes mixtes (publiques mais enrichies si connecté).
    """
    if credentials is None:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return {
            "user_id": payload.get("user_id"),
            "email":   payload.get("sub"),
            "role":    payload.get("role"),
        }
    except JWTError:
        return None