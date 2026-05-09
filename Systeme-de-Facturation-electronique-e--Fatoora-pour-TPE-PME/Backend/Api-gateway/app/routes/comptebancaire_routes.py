# app/router/comptebancaire_proxy_router.py
from fastapi import APIRouter, Request, Query
from app.core.config import settings
import httpx


router = APIRouter(prefix="/comptes-bancaires", tags=["Comptes Bancaires"])


def _headers(request: Request) -> dict:
    """Propage le token JWT du frontend vers le microservice"""
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}


@router.get("/")
async def get_all(
    request: Request, 
    page: int = Query(1, ge=1), 
    page_size: int = Query(10, ge=1, le=100)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/comptes-bancaires/",
            headers=_headers(request),
            params={"page": page, "page_size": page_size}
        )
    return response.json()


@router.post("/")
async def create(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ENTREPRISE_SERVICE_URL}/comptes-bancaires/",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.put("/{compte_id}")
async def update(compte_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.ENTREPRISE_SERVICE_URL}/comptes-bancaires/{compte_id}",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.delete("/{compte_id}")
async def delete(compte_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.ENTREPRISE_SERVICE_URL}/comptes-bancaires/{compte_id}",
            headers=_headers(request)
        )
    if response.status_code == 204:
        return Response(status_code=204)

    if not response.content:
        return Response(status_code=response.status_code)

    try:
        return response.json()
    except ValueError:
        return Response(content=response.text, status_code=response.status_code)