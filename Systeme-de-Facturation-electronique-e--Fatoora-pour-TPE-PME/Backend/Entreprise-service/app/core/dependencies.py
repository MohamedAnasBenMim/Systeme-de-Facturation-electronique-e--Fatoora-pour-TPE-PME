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
        print(f"[DEBUG] payload décodé : {payload}")
        raw_user_id = payload.get("user_id")
        email: str   = payload.get("sub")
        role: str    = payload.get("role")

        if raw_user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide — données manquantes",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id":       raw_user_id,
            "email":         email,
            "role":          role,
            "tenant_id":     payload.get("tenant_id"),
            "entreprise_id": payload.get("entreprise_id"),
            "plan":          payload.get("plan"),
        }

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


def get_current_entreprise_id(
    payload: dict = Depends(get_current_user)
) -> str:
    entreprise_id = payload.get("entreprise_id")
    if not entreprise_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="entreprise_id introuvable dans le token"
        )
    return str(entreprise_id)


def get_current_tenant_id(
    payload: dict = Depends(get_current_user)
) -> str:
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="tenant_id introuvable dans le token"
        )
    return str(tenant_id)