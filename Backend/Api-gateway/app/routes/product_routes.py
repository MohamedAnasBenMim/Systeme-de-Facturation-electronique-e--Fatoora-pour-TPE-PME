from fastapi import APIRouter, Request, UploadFile, File, Query
from fastapi.responses import Response, StreamingResponse
from app.core.config import settings
import httpx

router = APIRouter(prefix="/produits", tags=["produits"])


def _headers(request: Request) -> dict:
    return {"Authorization": request.headers.get("Authorization", "")}


def _proxy_response(resp: httpx.Response):
    return Response(
        content    = resp.content,
        status_code= resp.status_code,
        media_type = resp.headers.get("content-type", "application/json"),
    )



# CATÉGORIES

@router.get("/categories")
async def get_categories(request: Request):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{settings.PRODUIT_SERVICE_URL}/produits/categories", headers=_headers(request))
    return _proxy_response(r)


@router.post("/categories")
async def create_categorie(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{settings.PRODUIT_SERVICE_URL}/produits/categories", json=body, headers=_headers(request))
    return _proxy_response(r)


@router.delete("/categories/{categorie_id}")
async def delete_categorie(categorie_id: int, request: Request):
    async with httpx.AsyncClient() as c:
        r = await c.delete(f"{settings.PRODUIT_SERVICE_URL}/produits/categories/{categorie_id}", headers=_headers(request))
    return _proxy_response(r)


# ══════════════════════════════════════════════
# UNITÉS DE MESURE
# ══════════════════════════════════════════════
@router.get("/unites")
async def get_unites(request: Request):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{settings.PRODUIT_SERVICE_URL}/produits/unites", headers=_headers(request))
    return _proxy_response(r)


@router.post("/unites")
async def create_unite(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{settings.PRODUIT_SERVICE_URL}/produits/unites", json=body, headers=_headers(request))
    return _proxy_response(r)


# ══════════════════════════════════════════════
# BULK OPERATIONS
# ══════════════════════════════════════════════
@router.patch("/bulk/prix")
async def bulk_update_prix(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as c:
        r = await c.patch(f"{settings.PRODUIT_SERVICE_URL}/produits/bulk/prix", json=body, headers=_headers(request))
    return _proxy_response(r)


@router.post("/import")
async def import_csv(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{settings.PRODUIT_SERVICE_URL}/produits/import",
            files  = {"file": (file.filename, content, file.content_type)},
            headers= _headers(request),
            timeout= 60.0,
        )
    return _proxy_response(r)


@router.get("/export")
async def export_csv(request: Request):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{settings.PRODUIT_SERVICE_URL}/produits/export", headers=_headers(request))
    return Response(
        content    = r.content,
        status_code= r.status_code,
        media_type = "text/csv",
        headers    = {"Content-Disposition": "attachment; filename=catalogue.csv"},
    )


@router.get("/stockables")
async def get_stockables(request: Request):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{settings.PRODUIT_SERVICE_URL}/produits/stockables", headers=_headers(request))
    return _proxy_response(r)


# ══════════════════════════════════════════════
# CRUD PRODUIT
# ══════════════════════════════════════════════
@router.get("")
async def list_produits(request: Request):
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(
                f"{settings.PRODUIT_SERVICE_URL}/produits",
                params = dict(request.query_params),
                headers= _headers(request),
                timeout=30.0,
            )
        return _proxy_response(r)
    except httpx.ConnectError:
        return Response(
            content='{"detail": "Service produit indisponible"}',
            status_code=503,
            media_type="application/json"
        )
    except httpx.TimeoutException:
        return Response(
            content='{"detail": "Délai d\'attente dépassé"}',
            status_code=504,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Erreur: {str(e)}"}}',
            status_code=500,
            media_type="application/json"
        )


@router.post("")
async def create_produit(request: Request):
    try:
        body = await request.json()
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{settings.PRODUIT_SERVICE_URL}/produits", json=body, headers=_headers(request))
        return _proxy_response(r)
    except httpx.ConnectError:
        return Response(
            content='{"detail": "Service produit indisponible"}',
            status_code=503,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Erreur: {str(e)}"}}',
            status_code=500,
            media_type="application/json"
        )


@router.get("/{produit_id}")
async def get_produit(produit_id: int, request: Request):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{settings.PRODUIT_SERVICE_URL}/produits/{produit_id}", headers=_headers(request))
    return _proxy_response(r)


@router.patch("/{produit_id}")
async def update_produit(produit_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as c:
        r = await c.patch(f"{settings.PRODUIT_SERVICE_URL}/produits/{produit_id}", json=body, headers=_headers(request))
    return _proxy_response(r)


@router.delete("/{produit_id}")
async def delete_produit(produit_id: int, request: Request):
    async with httpx.AsyncClient() as c:
        r = await c.delete(f"{settings.PRODUIT_SERVICE_URL}/produits/{produit_id}", headers=_headers(request))
    return _proxy_response(r)


@router.get("/static/produits/{entreprise_id}/{filename}")
async def get_image(entreprise_id: int, filename: str, request: Request):
    async with httpx.AsyncClient() as c:
        r = await c.get(
            f"{settings.PRODUIT_SERVICE_URL}/produits/static/produits/{entreprise_id}/{filename}",
            headers=_headers(request),
        )
    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("content-type", "image/png"),
    )