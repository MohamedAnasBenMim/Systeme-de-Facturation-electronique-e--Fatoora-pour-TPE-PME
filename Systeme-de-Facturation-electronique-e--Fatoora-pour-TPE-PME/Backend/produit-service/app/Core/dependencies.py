from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        # --- EXTRACTION COMPLÈTE ---
        user_id = payload.get("user_id")
        email = payload.get("sub")
        role = payload.get("role")
        entreprise_id = payload.get("entreprise_id") # C'est ici que ça se passait
        tenant_id = payload.get("tenant_id")         # Utile pour ton architecture

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide — données manquantes",
            )

        # On retourne TOUTES les infos nécessaires pour les dépendances suivantes
        return {
            "user_id": user_id, 
            "email": email, 
            "role": role, 
            "entreprise_id": entreprise_id,
            "tenant_id": tenant_id
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
        )

def get_current_entreprise_id(
    current_user: dict = Depends(get_current_user)
) -> int:
    """
    Maintenant current_user contient bien la clé 'entreprise_id'
    """
    entreprise_id = current_user.get("entreprise_id")
    
    if entreprise_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Entreprise non associée à cet utilisateur dans le token",
        )
    return entreprise_id