from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    nom_entreprise: str          # ← ajouter
    email:          EmailStr
    password:       str
    role:           str = "USER"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    id: int
    email: str
    role: str
    tenant_id: str 
    message: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int