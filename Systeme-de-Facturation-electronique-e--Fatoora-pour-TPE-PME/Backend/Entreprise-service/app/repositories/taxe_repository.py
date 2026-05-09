# ms-entreprise/app/repositories/taxe_repository.py
from sqlalchemy.orm import Session
from app.models.taxe import Taxe, GroupeTaxe
from typing import List
import uuid

class TaxeRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── Taxes ──────────────────────────────────────────────
    def get_all(self, entreprise_id: int) -> List[Taxe]:
        return self.db.query(Taxe).filter(
            Taxe.entreprise_id == entreprise_id
        ).all()

    def get_by_id(self, taxe_id: str, entreprise_id: int) -> Taxe | None:
        return self.db.query(Taxe).filter(
            Taxe.id == taxe_id,
            Taxe.entreprise_id == entreprise_id
        ).first()

    def code_exists(self, code: str, entreprise_id: int) -> bool:
        return self.db.query(Taxe).filter(
            Taxe.code == code,
            Taxe.entreprise_id == entreprise_id
        ).first() is not None

    def create(self, entreprise_id: int, data: dict) -> Taxe:
        taxe = Taxe(id=uuid.uuid4(), entreprise_id=entreprise_id, **data)
        self.db.add(taxe)
        self.db.commit()
        self.db.refresh(taxe)
        return taxe

    def update(self, taxe: Taxe, data: dict) -> Taxe:
        for key, value in data.items():
            if value is not None:
                setattr(taxe, key, value)
        self.db.commit()
        self.db.refresh(taxe)
        return taxe

    def delete(self, taxe: Taxe) -> None:
        self.db.delete(taxe)
        self.db.commit()

    # ── Groupes ────────────────────────────────────────────
    def get_all_groupes(self, entreprise_id: int) -> List[GroupeTaxe]:
        return self.db.query(GroupeTaxe).filter(
            GroupeTaxe.entreprise_id == entreprise_id
        ).all()

    def get_groupe_by_id(self, groupe_id: str, entreprise_id: int) -> GroupeTaxe | None:
        return self.db.query(GroupeTaxe).filter(
            GroupeTaxe.id == groupe_id,
            GroupeTaxe.entreprise_id == entreprise_id
        ).first()

    def get_taxes_by_ids(self, taxe_ids: List[str], entreprise_id: int) -> List[Taxe]:
        return self.db.query(Taxe).filter(
            Taxe.id.in_(taxe_ids),
            Taxe.entreprise_id == entreprise_id
        ).all()

    def create_groupe(self, entreprise_id: int, nom: str, description: str | None, taxes: List[Taxe]) -> GroupeTaxe:
        groupe = GroupeTaxe(
            id            = uuid.uuid4(),
            entreprise_id = entreprise_id,
            nom           = nom,
            description   = description,
            taxes         = taxes,
        )
        self.db.add(groupe)
        self.db.commit()
        self.db.refresh(groupe)
        return groupe

    def update_groupe(self, groupe: GroupeTaxe, data: dict, taxes: List[Taxe] | None) -> GroupeTaxe:
        for key, value in data.items():
            if value is not None:
                setattr(groupe, key, value)
        if taxes is not None:
            groupe.taxes = taxes
        self.db.commit()
        self.db.refresh(groupe)
        return groupe

    def delete_groupe(self, groupe: GroupeTaxe) -> None:
        self.db.delete(groupe)
        self.db.commit()