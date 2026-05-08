from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.core.config import settings
import httpx

router = APIRouter(prefix="/devis", tags=["Devis"])


def _headers(request: Request) -> dict:
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}



@router.get("/")
async def get_all(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/devis/",
            headers=_headers(request)
        )
    return response.json()


@router.get("/{devis_id}")
async def get_by_id(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}",
            headers=_headers(request)
        )
    return response.json()


@router.post("/")
async def create(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/devis/",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.delete("/{devis_id}")
async def delete(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}",
            headers=_headers(request)
        )
    return response.json()



@router.put("/{devis_id}/envoyer")
async def envoyer(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}/envoyer",
            headers=_headers(request)
        )
    return response.json()


@router.put("/{devis_id}/accepter")
async def accepter(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}/accepter",
            headers=_headers(request)
        )
    return response.json()


@router.put("/{devis_id}/refuser")
async def refuser(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}/refuser",
            headers=_headers(request)
        )
    return response.json()


@router.put("/{devis_id}/statut")
async def update_statut(devis_id: int, request: Request):
    params = dict(request.query_params)
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}/statut",
            headers=_headers(request),
            params=params
        )
    return response.json()



@router.post("/{devis_id}/convertir/bon-commande")
async def convertir_en_bc(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}/convertir/bon-commande",
            headers=_headers(request)
        )
    return response.json()


@router.post("/{devis_id}/convertir/bon-livraison")
async def convertir_en_bl(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}/convertir/bon-livraison",
            headers=_headers(request)
        )
    return response.json()


@router.post("/{devis_id}/convertir/facture")
async def convertir_en_facture(devis_id: int, request: Request):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}/convertir/facture",
            headers=_headers(request)
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@router.get("/{devis_id}/pdf", response_class=StreamingResponse)
async def generate_devis_pdf(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/devis/{devis_id}/pdf",
            headers=_headers(request)
        )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Erreur lors de la génération du PDF")
    return StreamingResponse(
        iter([response.content]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=devis_{devis_id}.pdf"}
    )