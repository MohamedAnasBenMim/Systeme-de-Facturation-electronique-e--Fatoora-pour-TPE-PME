from fastapi import APIRouter, Request, Query, Response, HTTPException
from app.core.config import settings
import httpx
import os
from fastapi.responses import FileResponse

router = APIRouter(prefix="/factures", tags=["Factures"])


def _headers(request: Request) -> dict:
    """Propage le token JWT du frontend vers le microservice factures"""
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}


def _raise_if_error(response: httpx.Response):
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@router.get("/")
async def get_all(
    request: Request, 
    page: int = Query(1), 
    page_size: int = Query(10)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.FACTURE_SERVICE_URL}/factures/",
            headers=_headers(request),
            params={"page": page, "page_size": page_size}
        )
    _raise_if_error(response)
    return response.json()


@router.get("/{facture_id}")
async def get_by_id(facture_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.FACTURE_SERVICE_URL}/factures/{facture_id}",
            headers=_headers(request)
        )
    _raise_if_error(response)
    return response.json()


@router.get("/{facture_id}/detail")
async def get_detail(facture_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.FACTURE_SERVICE_URL}/factures/{facture_id}/detail",
            headers=_headers(request)
        )
    _raise_if_error(response)
    return response.json()


@router.post("/")
async def create(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.FACTURE_SERVICE_URL}/factures/",
            json=body,
            headers=_headers(request)
        )
    _raise_if_error(response)
    return response.json()


@router.post("/depuis-devis/{devis_id}")
async def create_from_devis(devis_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.FACTURE_SERVICE_URL}/factures/depuis-devis/{devis_id}",
            headers=_headers(request)
        )
    _raise_if_error(response)
    return response.json()


@router.put("/{facture_id}")
async def update(facture_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.FACTURE_SERVICE_URL}/factures/{facture_id}",
            json=body,
            headers=_headers(request)
        )
    _raise_if_error(response)
    return response.json()


@router.delete("/{facture_id}")
async def delete(facture_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.FACTURE_SERVICE_URL}/factures/{facture_id}",
            headers=_headers(request)
        )
    _raise_if_error(response)
    return response.json()


@router.get("/{facture_id}/pdf/download")
async def download_pdf(facture_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.FACTURE_SERVICE_URL}/factures/{facture_id}/pdf/download",
            headers=_headers(request)
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", "application/pdf"),
        headers={
            "Content-Disposition": response.headers.get(
                "content-disposition",
                f'attachment; filename="facture_{facture_id}.pdf"'
            )
        }
    )

@router.get("/{facture_id}/pdf/preview")
async def preview_pdf(facture_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.FACTURE_SERVICE_URL}/factures/{facture_id}/pdf/preview",
            headers=_headers(request),
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", "application/pdf"),
        headers={
            "Content-Disposition": response.headers.get(
                "content-disposition",
                f'inline; filename="facture_{facture_id}.pdf"'
            )
        },
    )
