from fastapi import APIRouter, Request, Query
from app.core.config import settings
import httpx

router = APIRouter(prefix="/users", tags=["Users"])

def _headers(request: Request) -> dict:
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}

@router.get("/")
async def get_all(request: Request, page: int = Query(1), page_size: int = Query(10)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.AUTH_SERVICE_URL}/users/",
            headers=_headers(request),
            params={"page": page, "page_size": page_size}
        )
    return response.json()

@router.get("/me")
async def get_me(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.USER_SERVICE_URL}/users/me",
            headers=_headers(request)
        )
    return response.json()

@router.get("/{user_id}")
async def get_by_id(user_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.AUTH_SERVICE_URL}/users/{user_id}",
            headers=_headers(request)
        )
    return response.json()

@router.put("/{user_id}")
async def update(user_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.AUTH_SERVICE_URL}/users/{user_id}",
            json=body,
            headers=_headers(request)
        )
    return response.json()

@router.delete("/{user_id}")
async def delete(user_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.AUTH_SERVICE_URL}/users/{user_id}",
            headers=_headers(request)
        )
    return response.json()

@router.put("/{user_id}/change-password")
async def change_password(user_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.AUTH_SERVICE_URL}/users/{user_id}/change-password",
            json=body,
            headers=_headers(request)
        )
    return response.json()