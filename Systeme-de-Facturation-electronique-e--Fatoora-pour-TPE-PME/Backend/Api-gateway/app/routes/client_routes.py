from fastapi import APIRouter, Request, Query
from app.core.config import settings
import httpx

router = APIRouter(prefix="/clients", tags=["Clients"])

def _headers(request: Request) -> dict:
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}

@router.get("/")
async def get_all(request: Request, page: int = Query(1), page_size: int = Query(10)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CLIENT_SERVICE_URL}/clients/",
            headers=_headers(request),
            params={"page": page, "page_size": page_size}
        )
    return response.json()

@router.get("/{client_id}")
async def get_by_id(client_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CLIENT_SERVICE_URL}/clients/{client_id}",
            headers=_headers(request)
        )
    return response.json()

@router.post("/")
async def create(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.CLIENT_SERVICE_URL}/clients/",
            json=body,
            headers=_headers(request)
        )
    return response.json()

@router.put("/{client_id}")
async def update(client_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.CLIENT_SERVICE_URL}/clients/{client_id}",
            json=body,
            headers=_headers(request)
        )
    return response.json()

@router.delete("/{client_id}")
async def delete(client_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.CLIENT_SERVICE_URL}/clients/{client_id}",
            headers=_headers(request)
        )
    return response.json()