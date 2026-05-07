from fastapi import APIRouter, Request
from fastapi.responses import Response
from app.core.config import settings
import httpx

router = APIRouter(prefix="/entreprises", tags=["Entreprises"])


def _headers(request: Request) -> dict:
    token = request.headers.get("Authorization", "")
    headers = {"Authorization": token}
    content_type = request.headers.get("Content-Type")
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def _proxy_response(resp: httpx.Response):
    content_type = resp.headers.get("content-type", "application/json")
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=content_type,
    )


@router.get("/")
async def get_all(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/mon-profil/complet",
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.get("/mon-profil")
async def get_mon_profil(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/mon-profil",
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.get("/mon-profil/complet")
async def get_mon_profil_complet(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/mon-profil/complet",
            headers=_headers(request),
        )
    return _proxy_response(response)

# TAXES
# gateway/entreprise_router.py — mets à jour toutes les URLs
@router.get("/taxes")
async def get_taxes(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/taxes",  
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.post("/taxes")
async def create_taxe(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ENTREPRISE_SERVICE_URL}/taxes",  
            json=body,
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.patch("/taxes/{taxe_id}")
async def update_taxe(taxe_id: str, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.ENTREPRISE_SERVICE_URL}/taxes/{taxe_id}",  # ✅
            json=body,
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.delete("/taxes/{taxe_id}")
async def delete_taxe(taxe_id: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.ENTREPRISE_SERVICE_URL}/taxes/{taxe_id}",  
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.get("/taxes/groupes")
async def get_groupes(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/taxes/groupes",  
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.post("/taxes/groupes")
async def create_groupe(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ENTREPRISE_SERVICE_URL}/taxes/groupes", 
            json=body,
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.patch("/taxes/groupes/{groupe_id}")
async def update_groupe(groupe_id: str, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.ENTREPRISE_SERVICE_URL}/taxes/groupes/{groupe_id}",  
            json=body,
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.delete("/taxes/groupes/{groupe_id}")
async def delete_groupe(groupe_id: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.ENTREPRISE_SERVICE_URL}/taxes/groupes/{groupe_id}", 
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.get("/cachet")
async def get_cachet(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/cachet",  
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.get("/cachet/image")
async def get_cachet_image(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/cachet/image",  
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.post("/cachet")
async def upload_cachet(request: Request):
    form = await request.form()
    files = None
    data  = {}
    if "file" in form:
        file  = form["file"]
        files = {"file": (file.filename, await file.read(), file.content_type)}
    if "nom" in form:
        data["nom"] = form["nom"]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ENTREPRISE_SERVICE_URL}/cachet",  
            files=files,
            data=data,
            headers={"Authorization": request.headers.get("Authorization", "")},
            timeout=30.0,
        )
    return _proxy_response(response)

@router.delete("/cachet")
async def delete_cachet(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.ENTREPRISE_SERVICE_URL}/cachet", 
            headers=_headers(request),
        )
    return _proxy_response(response)

@router.get("/{entreprise_id}")
async def get_by_id(entreprise_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/{entreprise_id}",
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.get("/{entreprise_id}/config")
async def get_config(entreprise_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/{entreprise_id}/config",
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.post("/")
async def create(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/",
            json=body,
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.put("/mon-profil")
async def update(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/mon-profil",
            json=body,
            headers=_headers(request),
        )
    return _proxy_response(response)


@router.post("/mon-profil/logo/{filename}")
async def upload_logo(request: Request):
    form = await request.form()
    files = None
    if "file" in form:
        file = form["file"]
        files = {"file": (file.filename, await file.read(), file.content_type)}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/mon-profil/logo/{filename}",
            files=files,
            headers=_headers(request),
        )
    return _proxy_response(response)