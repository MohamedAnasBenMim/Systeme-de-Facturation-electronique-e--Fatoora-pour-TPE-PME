"""
Toutes les communications vers les autres microservices.
Utilise httpx en mode async pour ne pas bloquer FastAPI.
"""
import httpx
from fastapi import HTTPException
from app.core.config import settings 
  


TIMEOUT = 5.0


async def get_client_by_id(client_id: int) -> dict:
    """Récupère les données complètes d'un client depuis le microservice client."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{settings.CLIENT_SERVICE_URL}/clients/{client_id}")
            if response.status_code == 404:
                print(f"⚠️  Client {client_id} non trouvé sur {settings.CLIENT_SERVICE_URL} — utilisation données par défaut")
                return {"id": client_id, "nom": f"Client #{client_id}"}
            if response.status_code != 200:
                print(f"❌ Erreur service client : {response.status_code}")
                return {"id": client_id, "nom": f"Client #{client_id}"}
            return response.json()
        except httpx.RequestError as e:
            print(f"❌ Service client inaccessible : {e} — utilisation données par défaut")
            return {"id": client_id, "nom": f"Client #{client_id}"}


async def get_entreprise_by_id(entreprise_id: int) -> dict:
    """Récupère les données complètes d'une entreprise depuis le microservice entreprise."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{settings.ENTREPRISE_SERVICE_URL}/entreprises/{entreprise_id}"
                )
            if response.status_code == 404:
                print(f"⚠️  Entreprise {entreprise_id} non trouvée sur {settings.ENTREPRISE_SERVICE_URL} — utilisation données par défaut")
                return {"id": entreprise_id, "nom": f"Entreprise #{entreprise_id}"}
            if response.status_code != 200:
                print(f"❌ Erreur service entreprise : {response.status_code}")
                return {"id": entreprise_id, "nom": f"Entreprise #{entreprise_id}"}
            return response.json()
        except httpx.RequestError as e:
            print(f"❌ Service entreprise inaccessible : {e} — utilisation données par défaut")
            return {"id": entreprise_id, "nom": f"Entreprise #{entreprise_id}"}


async def get_produit_by_id(product_id: int, token: str = None) -> dict:
    url = f"{settings.PRODUIT_SERVICE_URL}/produits/internal/{product_id}"
    
   
    print(f"🔍 Appel produit : GET {url}")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = await client.get(url, headers=headers)
            print(f"📦 Réponse produit {product_id} : {response.status_code} → {response.text[:200]}")
        except httpx.RequestError as e:
            print(f"❌ Service produit inaccessible : {e}")
            # ✅ Tolérant — ne bloque pas la création de facture
            return {"designation": f"Produit #{product_id}"}

    if response.status_code == 404:
        print(f"⚠️  Produit {product_id} non trouvé sur {url} — utilisation désignation par défaut")
        # ✅ Tolérant — désignation par défaut au lieu de bloquer
        return {"designation": f"Produit #{product_id}"}
        
    if response.status_code != 200:
        print(f"❌ Erreur service produit : {response.status_code}")
        return {"designation": f"Produit #{product_id}"}

    return response.json()


async def get_devis_by_id(devis_id: int) -> dict:
    """Récupère un devis complet depuis le microservice devis."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{settings.DEVIS_SERVICE_URL}/devis/internal/{devis_id}")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service devis indisponible")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Devis {devis_id} introuvable")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erreur service devis")

    return response.json()