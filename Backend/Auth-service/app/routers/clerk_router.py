# ms-auth/app/api/clerk_router.py
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.clerk_service import ClerkService
from pydantic import BaseModel

router = APIRouter(prefix="/auth/clerk", tags=["Clerk OAuth"])


def get_service(db: Session = Depends(get_db)):
    return ClerkService(db)


# ── Webhook Clerk (appelé par Clerk, pas le frontend) ──
@router.post("/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def clerk_webhook(
    request: Request,
    service: ClerkService = Depends(get_service),
):
    payload = await request.body()
    headers = {
        "svix-id":        request.headers.get("svix-id"),
        "svix-timestamp": request.headers.get("svix-timestamp"),
        "svix-signature": request.headers.get("svix-signature"),
    }

    try:
        event = service.verify_webhook(payload, headers)
    except ValueError:
        raise HTTPException(status_code=400, detail="Signature invalide")

    event_type = event.get("type")
    if event_type == "user.created":
        await service.handle_user_created(event["data"])
    # Ajoute d'autres events ici si besoin (user.deleted, etc.)


# ── Échange du token Clerk → JWT interne ──
class ClerkTokenRequest(BaseModel):
    clerk_token: str


@router.post("/token", response_model=dict)
async def exchange_token(
    body: ClerkTokenRequest,
    service: ClerkService = Depends(get_service),
):
    try:
        return await service.exchange_clerk_token(body.clerk_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))