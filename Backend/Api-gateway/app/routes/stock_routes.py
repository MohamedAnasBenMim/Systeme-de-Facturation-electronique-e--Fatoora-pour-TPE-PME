from fastapi import APIRouter, Request, Response
from app.core.config import settings
import httpx

router = APIRouter(prefix="/stock", tags=["Stock Integration"])


def _headers(request: Request) -> dict:
    headers = {"Authorization": request.headers.get("Authorization", "")}
    if settings.INTEGRATION_SERVICE_SECRET:
        headers["X-Internal-Service-Secret"] = settings.INTEGRATION_SERVICE_SECRET
    return headers


def _proxy_response(resp: httpx.Response):
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
    )


@router.get("/produits")
async def list_stock_products(request: Request):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{settings.STOCK_SERVICE_URL}/api/v1/produits",
            params=dict(request.query_params),
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.get("/produits/{produit_id}")
async def get_stock_product(produit_id: int, request: Request):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{settings.STOCK_SERVICE_URL}/api/v1/produits/{produit_id}",
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.get("/stocks")
async def list_stock_levels(request: Request):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{settings.STOCK_SERVICE_URL}/api/v1/stocks",
            params=dict(request.query_params),
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.get("/stocks/produit/{produit_id}")
async def get_product_stock_levels(produit_id: int, request: Request):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{settings.STOCK_SERVICE_URL}/api/v1/stocks/produit/{produit_id}",
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.post("/mouvements")
async def create_stock_movement(request: Request):
    body = await request.json()
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{settings.MOUVEMENT_SERVICE_URL}/api/v1/mouvements",
            json=body,
            headers=_headers(request),
        )
    return _proxy_response(response)
