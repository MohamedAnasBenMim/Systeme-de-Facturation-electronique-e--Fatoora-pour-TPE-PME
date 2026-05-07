from fastapi import APIRouter, Request, Query, Response, HTTPException
from app.core.config import settings
import httpx
import os
from fastapi.responses import FileResponse

router = APIRouter(prefix="/achats", tags=["Achats"])


def _headers(request: Request) -> dict:
    """Propage le token JWT du frontend vers le microservice achats"""
    token = request.headers.get("Authorization", "")
    return {"Authorization": token}


# FOURNISSEURS 

@router.post("/fournisseurs")
async def create_fournisseur(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ACHATS_SERVICE_URL}/achats/fournisseurs",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.get("/fournisseurs")
async def list_fournisseurs(
    request: Request,
    actifs_seulement: bool = Query(True)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/fournisseurs",
            headers=_headers(request),
            params={"actifs_seulement": actifs_seulement}
        )
    return response.json()


@router.get("/fournisseurs/{fournisseur_id}")
async def get_fournisseur(fournisseur_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/fournisseurs/{fournisseur_id}",
            headers=_headers(request)
        )
    return response.json()


@router.put("/fournisseurs/{fournisseur_id}")
async def update_fournisseur(fournisseur_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.ACHATS_SERVICE_URL}/achats/fournisseurs/{fournisseur_id}",
            json=body,
            headers=_headers(request)
        )
    return response.json()


# ============ BONS DE COMMANDE ============

@router.post("/bons-commande")
async def create_bc(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ACHATS_SERVICE_URL}/achats/bons-commande",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.get("/bons-commande")
async def list_bcs(
    request: Request,
    entreprise_id: int = Query(None)
):
    params = {}
    if entreprise_id:
        params["entreprise_id"] = entreprise_id
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/bons-commande",
            headers=_headers(request),
            params=params
        )
    return response.json()


@router.get("/bons-commande/{bc_id}")
async def get_bc(bc_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/bons-commande/{bc_id}",
            headers=_headers(request)
        )
    return response.json()


@router.post("/bons-commande/{bc_id}/confirmer")
async def confirm_bc(bc_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ACHATS_SERVICE_URL}/achats/bons-commande/{bc_id}/confirmer",
            headers=_headers(request)
        )
    return response.json()


# ============ RÉCEPTIONS ============

@router.post("/receptions")
async def create_reception(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ACHATS_SERVICE_URL}/achats/receptions",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.get("/receptions/{reception_id}")
async def get_reception(reception_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/receptions/{reception_id}",
            headers=_headers(request)
        )
    return response.json()


# ============ BONS DE RETOUR ============

@router.post("/bons-retour")
async def create_bon_retour(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ACHATS_SERVICE_URL}/achats/bons-retour",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.post("/bons-retour/{br_id}/valider")
async def validate_bon_retour(br_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ACHATS_SERVICE_URL}/achats/bons-retour/{br_id}/valider",
            headers=_headers(request)
        )
    return response.json()


# ============ FACTURES FOURNISSEUR ============

@router.post("/factures-fournisseur")
async def create_facture_fournisseur(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ACHATS_SERVICE_URL}/achats/factures-fournisseur",
            json=body,
            headers=_headers(request)
        )
    return response.json()


@router.get("/factures-fournisseur")
async def list_factures_fournisseur(
    request: Request,
    entreprise_id: int = Query(None)
):
    params = {}
    if entreprise_id:
        params["entreprise_id"] = entreprise_id
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/factures-fournisseur",
            headers=_headers(request),
            params=params
        )
    return response.json()


@router.get("/factures-fournisseur/{facture_id}")
async def get_facture_fournisseur(facture_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/factures-fournisseur/{facture_id}",
            headers=_headers(request)
        )
    return response.json()


# ============ LITIGES ============

@router.get("/litiges")
async def list_litiges(
    request: Request,
    entreprise_id: int = Query(None)
):
    params = {}
    if entreprise_id:
        params["entreprise_id"] = entreprise_id
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/litiges",
            headers=_headers(request),
            params=params
        )
    return response.json()


@router.get("/litiges/{facture_id}")
async def get_litige(facture_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/litiges/{facture_id}",
            headers=_headers(request)
        )
    return response.json()


@router.post("/litiges/{facture_id}/resoudre")
async def resolve_litige(facture_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ACHATS_SERVICE_URL}/achats/litiges/{facture_id}/resoudre",
            json=body,
            headers=_headers(request)
        )
    return response.json()


# ============ STATISTIQUES ============

@router.get("/stats/global")
async def stats_achats_global(
    request: Request,
    entreprise_id: int = Query(...),
    date_debut: str = Query(None),
    date_fin: str = Query(None)
):
    params = {"entreprise_id": entreprise_id}
    if date_debut:
        params["date_debut"] = date_debut
    if date_fin:
        params["date_fin"] = date_fin
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/stats/global",
            headers=_headers(request),
            params=params
        )
    return response.json()


@router.get("/stats/fournisseurs-fideles")
async def stats_fournisseurs_fideles(
    request: Request,
    entreprise_id: int = Query(...),
    limite: int = Query(5)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/stats/fournisseurs-fideles",
            headers=_headers(request),
            params={"entreprise_id": entreprise_id, "limite": limite}
        )
    return response.json()


# ============ AUDIT TRAIL ============

@router.get("/audit-trail/bon-commande/{bc_id}")
async def get_audit_trail_bc(bc_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/audit-trail/bon-commande/{bc_id}",
            headers=_headers(request)
        )
    return response.json()


@router.get("/audit-trail/facture/{facture_id}")
async def get_audit_trail_facture(facture_id: int, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.ACHATS_SERVICE_URL}/achats/audit-trail/facture/{facture_id}",
            headers=_headers(request)
        )
    return response.json()