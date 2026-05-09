from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role import Role
from app.schemas.role_schema import RoleCreate, RoleUpdate

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Role]:
        return self.db.query(Role).all()

    def get_by_id(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def create(self, data: RoleCreate) -> Role:
        role = Role(**data.model_dump())
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update(self, role: Role, data: RoleUpdate) -> Role:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete(self, role: Role) -> None:
        self.db.delete(role)
        self.db.commit()