from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.security import verify_token

security = HTTPBearer()

def get_current_user(token=Depends(security)):
    payload = verify_token(token.credentials)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {
        "id": payload.get("sub"),
        "nom": payload.get("nom"),
        "prenom": payload.get("prenom"),
        "email": payload.get("email"),
    }