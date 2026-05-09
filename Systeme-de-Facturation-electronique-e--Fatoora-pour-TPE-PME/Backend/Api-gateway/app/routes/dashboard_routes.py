# dashboard_routes.py
import asyncio
import httpx
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import date
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
bearer_scheme = HTTPBearer()

FACTURE_SERVICE_URL  = settings.FACTURE_SERVICE_URL
DEPENSES_SERVICE_URL = settings.DEPENSES_SERVICE_URL
ENTREPRISE_SERVICE_URL = settings.ENTREPRISE_SERVICE_URL

# ─── Helper fetch ─────────────────────────────────────────────────
async def fetch(client: httpx.AsyncClient, url: str, params: dict, token: str = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = await client.get(url, params=params, headers=headers, timeout=10.0)
        print(f"[FETCH] {url} → {r.status_code}")
        if r.status_code >= 400:
            print(f"[FETCH] Erreur body: {r.text}")
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=502, detail=f"Service injoignable : {url}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Erreur [{url}] → {e.response.status_code}: {e.response.text}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=502, detail=f"Timeout : {url}")

# ─── Helper entreprise_id ─────────────────────────────────────────
def get_entreprise_id_from_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"[TOKEN PAYLOAD] {payload}")

        entreprise_id = payload.get("entreprise_id")

        if not entreprise_id:
            user_id = payload.get("user_id")
            try:
                r = httpx.get(
                    f"{ENTREPRISE_SERVICE_URL}/entreprises/by-owner/{user_id}",
                    timeout=5.0
                )
                print(f"[GATEWAY] by-owner → {r.status_code} : {r.text}")
                if r.status_code == 200:
                    entreprise_id = r.json().get("id")
            except Exception as e:
                print(f"[GATEWAY] Erreur appel entreprise-service : {e}")

        if not entreprise_id:
            print("[GATEWAY] Entreprise introuvable, utilisation de l'entreprise locale #1")
            entreprise_id = 1

        return int(entreprise_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

# ─── Routes ───────────────────────────────────────────────────────
@router.get("/stats")
async def dashboard_stats(
    date_debut: Optional[date] = None,
    date_fin:   Optional[date] = None,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    entreprise_id = get_entreprise_id_from_token(token)

    params_communs = {
        "entreprise_id": entreprise_id,
        **({"date_debut": str(date_debut)} if date_debut else {}),
        **({"date_fin":   str(date_fin)}   if date_fin   else {}),
    }

    async with httpx.AsyncClient() as client:
        factures_stats, depenses_stats = await asyncio.gather(
            fetch(client, f"{FACTURE_SERVICE_URL}/factures/stats/global",  params_communs, token),
            fetch(client, f"{DEPENSES_SERVICE_URL}/depenses/stats/global", params_communs, token),
        )

    profit = factures_stats["revenus_encaisses"] - depenses_stats["total_depenses_payees"]

    return {
        "revenus":              factures_stats["revenus_encaisses"],
        "chiffre_affaires":     factures_stats["chiffre_affaires"],
        "creances_en_attente":  factures_stats["creances_en_attente"],
        "nombre_factures":      factures_stats["nombre_factures"],
        "depenses":             depenses_stats["total_depenses_payees"],
        "depenses_en_attente":  depenses_stats["total_depenses_en_attente"],
        "repartition_depenses": depenses_stats["repartition_par_categorie"],
        "profit":               round(profit, 3),
    }


@router.get("/clients-fideles")
async def dashboard_clients_fideles(
    limite: int = 5,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    entreprise_id = get_entreprise_id_from_token(token)

    async with httpx.AsyncClient() as client:
        return await fetch(
            client,
            f"{FACTURE_SERVICE_URL}/factures/stats/clients-fideles",
            {"entreprise_id": entreprise_id, "limite": limite},
            token,
        )


@router.get("/stats/projet/{product_id}")
async def dashboard_stats_projet(
    product_id:    int,
    entreprise_id: int = Query(...),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials

    async with httpx.AsyncClient() as client:
        factures, depenses = await asyncio.gather(
            fetch(client, f"{FACTURE_SERVICE_URL}/factures/stats/par-projet/{product_id}",  {"entreprise_id": entreprise_id}, token),
            fetch(client, f"{DEPENSES_SERVICE_URL}/depenses/stats/par-projet/{product_id}", {"entreprise_id": entreprise_id}, token),
        )

    return {
        "product_id":      product_id,
        "total_facture":   factures["total_facture"],
        "total_encaisse":  factures["total_encaisse"],
        "total_depenses":  depenses["total_depenses"],
        "depenses_payees": depenses["depenses_payees"],
        "marge_nette":     round(factures["total_encaisse"] - depenses["depenses_payees"], 3),
    }
