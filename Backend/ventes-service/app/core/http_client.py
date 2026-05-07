"""Client HTTP centralisé pour les appels inter-services."""
import httpx
from app.core.config import settings


class HttpClient:

    @staticmethod
    async def get(url: str, params: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def post(url: str, data: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def put(url: str, data: dict = None, params: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
            response = await client.put(url, json=data, params=params)
            response.raise_for_status()
            return response.json()