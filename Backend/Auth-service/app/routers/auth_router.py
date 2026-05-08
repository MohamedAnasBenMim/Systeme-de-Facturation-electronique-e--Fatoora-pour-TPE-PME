# ms-auth/app/api/auth_router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, RegisterResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentification"])

def get_service(db: Session = Depends(get_db)):
    return AuthService(db)

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, service=Depends(get_service)):
    return await service.register(data)   # ← async  appel HTTP interne

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, service=Depends(get_service)):
    return service.login(data)            