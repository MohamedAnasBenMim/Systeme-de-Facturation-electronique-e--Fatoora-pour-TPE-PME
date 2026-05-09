from fastapi import APIRouter, Request, Query, Response,HTTPException
from fastapi.responses import StreamingResponse
from app.core.config import settings
import httpx

router = APIRouter(prefix="/bon-livraison", tags=["Bon de Livraison"])
HTTP_TIMEOUT = httpx.Timeout(30.0)


def _headers(request: Request) -> dict:
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}


@router.post("/")
async def create(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/",
            json=body,
            headers=_headers(request)
            
        )
    
    if response.status_code == 204 or not response.content:
        return Response(status_code=response.status_code)
    
    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
    
    return response.json()

@router.get("/")
async def get_all(
    request: Request,
    page: int = Query(1),
    page_size: int = Query(10)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/",
            headers=_headers(request),
            params={"page": page, "page_size": page_size}
        )
    return response.json()


@router.get("/{bl_id}")
async def get_by_id(bl_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/{bl_id}",
            headers=_headers(request)
        )
    return response.json()


@router.delete("/{bl_id}")
async def delete(bl_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/{bl_id}",
            headers=_headers(request)
        )
    return Response(status_code=response.status_code)




@router.post("/depuis-bc/{bc_id}")
async def create_depuis_bc(bc_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/depuis-bc/{bc_id}",
            headers=_headers(request)
        )
    return response.json()


@router.post("/depuis-devis/{devis_id}")
async def create_depuis_devis(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/depuis-devis/{devis_id}",
            headers=_headers(request)
        )
    return response.json()


# ──────────────────────────────────────────────────────────────
# ACTIONS
# ──────────────────────────────────────────────────────────────

@router.post("/convertir/facture-groupee")
async def convertir_groupe_en_facture(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/convertir/facture-groupee",
            json=body,
            headers=_headers(request)
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@router.put("/{bl_id}/confirmer")
async def confirmer(bl_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/{bl_id}/confirmer",
            headers=_headers(request)
        )
    return response.json()


@router.put("/{bl_id}/annuler")
async def annuler(bl_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/{bl_id}/annuler",
            headers=_headers(request)
        )
    return response.json()


@router.put("/{bl_id}/quantites")
async def mettre_a_jour_quantites(bl_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/{bl_id}/quantites",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.post("/{bl_id}/partiel")
async def creer_bl_partiel(bl_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/{bl_id}/partiel",
            headers=_headers(request)
        )
    return response.json()


@router.get("/{bl_id}/pdf", response_class=StreamingResponse)
async def generate_bl_pdf(bl_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.VENTES_SERVICE_URL}/bon-livraison/{bl_id}/pdf",
            headers=_headers(request)
        )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Erreur lors de la génération du PDF")
    return StreamingResponse(
        iter([response.content]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=bon_livraison_{bl_id}.pdf"}
    )




@router.post("/{bl_id}/convertir/facture")
async def convertir_en_facture(bl_id: int, request: Request):
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                f"{settings.VENTES_SERVICE_URL}/bon-livraison/{bl_id}/convertir/facture",
                headers=_headers(request)
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Timeout lors de la conversion du BL en facture. Réessayez."
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Impossible de joindre ventes-service: {str(e)}"
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


