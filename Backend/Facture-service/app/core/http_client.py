"""
Toutes les communications vers les autres microservices.
Utilise httpx en mode async pour ne pas bloquer FastAPI.
"""
import httpx
from fastapi import HTTPException
from app.core.config import settings 
  


TIMEOUT = 5.0


def _integration_headers(token: str = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if settings.INTEGRATION_SERVICE_SECRET:
        headers["X-Internal-Service-Secret"] = settings.INTEGRATION_SERVICE_SECRET
    return headers


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


async def get_stock_produit_by_id(product_id: int, token: str = None) -> dict | None:
    """Récupère un produit depuis le projet Stock. None = non géré par Stock."""
    url = f"{settings.STOCK_SERVICE_URL}/api/v1/produits/{product_id}"
    headers = _integration_headers(token)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(url, headers=headers)
        except httpx.RequestError as e:
            print(f"❌ Service stock inaccessible pour produit {product_id} : {e}")
            return None

    if response.status_code == 404:
        return None
    if response.status_code != 200:
        print(f"❌ Erreur service stock produit {product_id} : {response.status_code}")
        return None
    return response.json()


async def get_stock_disponible(
    product_id: int,
    token: str = None,
    source_id: int | None = None,
    source_type: str | None = None,
) -> float | None:
    """Retourne la quantité disponible dans Stock. None = stock indisponible/non géré."""
    source_id = source_id or settings.STOCK_DEFAULT_SOURCE_ID
    source_type = (source_type or settings.STOCK_DEFAULT_SOURCE_TYPE).upper()
    params = {"produit_id": product_id}
    if source_type == "MAGASIN":
        params["magasin_id"] = source_id
    else:
        params["depot_id"] = source_id

    headers = _integration_headers(token)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(
                f"{settings.STOCK_SERVICE_URL}/api/v1/stocks",
                params=params,
                headers=headers,
            )
        except httpx.RequestError as e:
            print(f"❌ Service stock inaccessible pour disponibilité produit {product_id} : {e}")
            return None

    if response.status_code == 404:
        return None
    if response.status_code != 200:
        print(f"❌ Erreur disponibilité stock produit {product_id} : {response.status_code}")
        return None

    stocks = response.json()
    if not isinstance(stocks, list):
        return None
    return float(sum(float(s.get("quantite") or 0) for s in stocks))


async def creer_sortie_stock_depuis_facture(
    *,
    product_id: int,
    designation: str,
    quantite: float,
    facture_ref: str,
    token: str = None,
    source_id: int | None = None,
    source_type: str | None = None,
) -> dict:
    """Crée un mouvement SORTIE dans le projet Stock pour une facture validée."""
    source_id = source_id or settings.STOCK_DEFAULT_SOURCE_ID
    source_type = (source_type or settings.STOCK_DEFAULT_SOURCE_TYPE).upper()
    headers = _integration_headers(token)
    payload = {
        "type_mouvement": "sortie",
        "produit_id": product_id,
        "produit_nom": designation,
        "quantite": quantite,
        "entrepot_source_id": source_id,
        "source_type": source_type,
        "reference": facture_ref,
        "motif": "Vente facturée via e-Fatoora",
        "note": "Mouvement généré automatiquement après validation de facture.",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{settings.MOUVEMENT_SERVICE_URL}/api/v1/mouvements",
                json=payload,
                headers=headers,
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service mouvement stock indisponible")

    if response.status_code >= 400:
        detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "La facture est validée mais la sortie stock a échoué.",
                "stock_error": detail,
                "facture_ref": facture_ref,
            },
        )
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
