from fastapi import APIRouter, Request, Query
from app.core.config import settings
import httpx

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def _headers(request: Request) -> dict:
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}

@router.get("/")
async def get_all(request: Request, page: int = Query(1), page_size: int = Query(10)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/",
            headers=_headers(request),
            params={"page": page, "page_size": page_size}
        )
    return response.json()

@router.get("/non-lues")
async def get_non_lues(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/non-lues",
            headers=_headers(request)
        )
    return response.json()

@router.put("/{notification_id}/lue")
async def marquer_lue(notification_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/{notification_id}/lue",
            headers=_headers(request)
        )
    return response.json()

@router.put("/toutes-lues")
async def marquer_toutes_lues(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/toutes-lues",
            headers=_headers(request)
        )
    return response.json()

@router.delete("/{notification_id}")
async def delete(notification_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/{notification_id}",
            headers=_headers(request)
        )
    return response.json()