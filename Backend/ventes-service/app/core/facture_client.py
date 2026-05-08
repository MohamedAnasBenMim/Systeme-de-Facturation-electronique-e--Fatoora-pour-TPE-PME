import httpx
from fastapi import HTTPException
from app.core.config import settings


class FacturesClient:

    def __init__(self):
        self.base_url = settings.FACTURE_SERVICE_URL
        self.timeout  = httpx.Timeout(10.0)

    #créer une facture depuis un document source 

    async def creer_depuis_devis(self, devis_id: int, payload: dict | None = None) -> dict:
        return await self._post(f"/factures/depuis-devis/{devis_id}", payload)

    async def creer_depuis_bc(self, payload: dict) -> dict:
        return await self._post("/factures/", payload)

    async def creer_depuis_bl(self, payload: dict) -> dict:
        return await self._post("/factures/", payload)

    async def creer_groupee_depuis_bls(self, payload: dict) -> dict:
       
        return await self._post("/factures/groupee", payload)

    async def get_client(self, client_id: int) -> dict:
        return await self._get(f"/clients/{client_id}")

    # ------------------------------------------------------------------
    # Interne
    # ------------------------------------------------------------------

    async def _get(self, path: str) -> dict:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail="Le microservice factures-service ne répond pas (timeout)."
                )
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Erreur factures-service : {e.response.text}"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Impossible de joindre factures-service : {str(e)}"
                )

    async def _post(self, path: str, payload: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if payload is None:
                    response = await client.post(url)
                else:
                    response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail="Le microservice factures-service ne répond pas (timeout)."
                )
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Erreur factures-service : {e.response.text}"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Impossible de joindre factures-service : {str(e)}"
                )