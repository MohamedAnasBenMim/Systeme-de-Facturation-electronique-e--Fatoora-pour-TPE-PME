from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status
from app.repositories.role_repository import RoleRepository
from app.schemas.role_schema import RoleCreate, RoleUpdate, RoleResponse

class RoleService:
    def __init__(self, db: Session):
        self.repo = RoleRepository(db)

    def get_all(self) -> List[RoleResponse]:
        return self.repo.get_all()

    def get_by_id(self, role_id: int) -> RoleResponse:
        role = self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    def create(self, data: RoleCreate) -> RoleResponse:
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=409, detail="Role name already exists")
        return self.repo.create(data)

    def update(self, role_id: int, data: RoleUpdate) -> RoleResponse:
        role = self.get_by_id(role_id)
        return self.repo.update(role, data)

    def delete(self, role_id: int) -> None:
        role = self.get_by_id(role_id)
        self.repo.delete(role)