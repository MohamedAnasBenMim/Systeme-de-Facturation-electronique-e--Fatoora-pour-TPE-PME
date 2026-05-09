import httpx
import logging
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)


class TokenManager:

    _token: str = None

    @classmethod
    async def get_token(cls) -> str:
        if not cls._token:
            cls._token = await cls._login()
        return cls._token

    @classmethod
    def invalidate(cls):
        cls._token = None

    @classmethod
    async def _login(cls) -> str:
        logger.info("[TokenManager] Connexion au service auth...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.AUTH_SERVICE_URL}/api/auth/login",
                    json={
                        "email"   : settings.SERVICE_EMAIL,
                        "password": settings.SERVICE_PASSWORD
                    }
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=503,
                        detail="Erreur auth service interne"
                    )
                data = response.json()
                logger.info("[TokenManager] Token obtenu")
                return data["access_token"]

        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Service auth inaccessible"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Service auth timeout"
            )


class HttpClient:

    @staticmethod
    async def _headers() -> dict:
        token = await TokenManager.get_token()
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    async def get(url: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url, headers=await HttpClient._headers()
                )
                if response.status_code == 401:
                    TokenManager.invalidate()
                    response = await client.get(
                        url, headers=await HttpClient._headers()
                    )
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail="Ressource introuvable"
                    )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Erreur microservice : {response.text}"
                    )
                return response.json()

        except HTTPException:
            raise
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Service indisponible")

    @staticmethod
    async def post(url: str, data: dict) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url, json=data, headers=await HttpClient._headers()
                )
                if response.status_code == 401:
                    TokenManager.invalidate()
                    response = await client.post(
                        url, json=data, headers=await HttpClient._headers()
                    )
                if response.status_code not in (200, 201):
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Erreur microservice : {response.text}"
                    )
                return response.json()

        except HTTPException:
            raise
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Service indisponible")