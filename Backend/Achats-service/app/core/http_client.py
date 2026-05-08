"""
Toutes les communications vers les autres microservices.
Utilise httpx en mode async pour ne pas bloquer FastAPI.
"""
import httpx
from fastapi import HTTPException
from app.core.config import settings


TIMEOUT = 5.0


async def get_fournisseur_by_id(fournisseur_id: int) -> dict:
    """Récupère les données complètes d'un fournisseur depuis le microservice client ou entreprise."""
    # Pour simplifier, on suppose que les fournisseurs sont des entreprises
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/{fournisseur_id}")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service entreprise indisponible")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Fournisseur {fournisseur_id} introuvable")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erreur service entreprise")

    return response.json()


async def get_entreprise_by_id(entreprise_id: int) -> dict:
    """Récupère les données complètes d'une entreprise depuis le microservice entreprise."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/{entreprise_id}")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service entreprise indisponible")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Entreprise {entreprise_id} introuvable")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erreur service entreprise")

    return response.json()


async def get_produit_by_id(product_id: int, token: str = None) -> dict:
    """Récupère la désignation et les infos d'un produit depuis le microservice produit."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{settings.PRODUIT_SERVICE_URL}/produits/{product_id}", headers=headers)
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service produit indisponible")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Produit {product_id} introuvable")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erreur service produit")

    return response.json()