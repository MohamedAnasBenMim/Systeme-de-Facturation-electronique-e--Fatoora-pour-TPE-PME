from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.services.role_service import RoleService
from app.schemas.role_schema import RoleCreate, RoleUpdate, RoleResponse

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=List[RoleResponse])
def get_all_roles(db: Session = Depends(get_db)):
    return RoleService(db).get_all()

@router.get("/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    return RoleService(db).get_by_id(role_id)

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(data: RoleCreate, db: Session = Depends(get_db)):
    return RoleService(db).create(data)

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    return RoleService(db).update(role_id, data)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    RoleService(db).delete(role_id)