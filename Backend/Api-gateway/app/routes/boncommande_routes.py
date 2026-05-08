from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.core.config import settings
import httpx

router = APIRouter(prefix="/bon-commande", tags=["Bon de Commande"])


def _headers(request: Request) -> dict:
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}




@router.get("/")
async def get_all(
    request: Request,
    page: int = Query(1),
    page_size: int = Query(10)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/bon-commande/",
            headers=_headers(request),
            params={"page": page, "page_size": page_size}
        )
    return response.json()


@router.get("/{bc_id}")
async def get_by_id(bc_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/bon-commande/{bc_id}",
            headers=_headers(request)
        )
    return response.json()


@router.post("/depuis-devis")
async def create_depuis_devis(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-commande/depuis-devis",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.post("/manuel")
async def create_manuel(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-commande/manuel",
            json=body,
            headers=_headers(request)
        )
    return response.json()


# ──────────────────────────────────────────────────────────────
# STATUTS
# ──────────────────────────────────────────────────────────────

@router.put("/{bc_id}/statut")
async def changer_statut(bc_id: int, request: Request):
    params = dict(request.query_params)
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.VENTES_SERVICE_URL}/bon-commande/{bc_id}/statut",
            headers=_headers(request),
            params=params
        )
    return response.json()



@router.post("/{bc_id}/convertir/bon-livraison")
async def convertir_en_bl(bc_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-commande/{bc_id}/convertir/bon-livraison",
            headers=_headers(request)
        )
    return response.json()


@router.post("/{bc_id}/convertir/facture")
async def convertir_en_facture(bc_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-commande/{bc_id}/convertir/facture",
            headers=_headers(request)
        )
    return response.json()


@router.get("/{bc_id}/pdf", response_class=StreamingResponse)
async def generate_bc_pdf(bc_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/bon-commande/{bc_id}/pdf",
            headers=_headers(request)
        )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Erreur lors de la génération du PDF")
    return StreamingResponse(
        iter([response.content]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=bon_commande_{bc_id}.pdf"}
    )