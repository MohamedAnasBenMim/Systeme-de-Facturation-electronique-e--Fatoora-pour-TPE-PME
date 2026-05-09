from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
import httpx

router = APIRouter(prefix="/auth", tags=["Auth"])

async def proxy(method: str, url: str, request: Request):
    try:
        # ✅ Lire le body brut et le forwarder tel quel
        body = await request.body()
        headers = {
            "Content-Type": request.headers.get("Content-Type", "application/json"),
        }
        
        #  Forwarder aussi le token si présent
        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await getattr(client, method)(
                url,
                content=body,      
                headers=headers,
            )

        try:
            content = response.json()
        except Exception:
            content = {"detail": response.text or "Réponse vide"}

        return JSONResponse(content=content, status_code=response.status_code)

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"Service indisponible : {url}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Timeout : {url}")


@router.post("/register")
async def register(request: Request):
    return await proxy("post", f"{settings.AUTH_SERVICE_URL}/auth/register", request)


@router.post("/login")
async def login(request: Request):
    return await proxy("post", f"{settings.AUTH_SERVICE_URL}/auth/login", request)