from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.role_schema import RoleResponse

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
    role_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    role: Optional[RoleResponse] = None
    password: str

    model_config = {"from_attributes": True}