# ms-entreprise/app/services/taxe_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.taxe_repository import TaxeRepository
from app.schemas.taxe import TaxeCreate, TaxeUpdate, GroupeTaxeCreate, GroupeTaxeUpdate

class TaxeService:
    def __init__(self, db: Session):
        self.repo = TaxeRepository(db)

    # ── Taxes ──────────────────────────────────────────────
    def list_taxes(self, entreprise_id: int):
        return self.repo.get_all(entreprise_id)

    def create_taxe(self, entreprise_id: int, data: TaxeCreate):
        if self.repo.code_exists(data.code, entreprise_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Une taxe avec le code '{data.code}' existe déjà"
            )
        return self.repo.create(entreprise_id, data.model_dump())

    def update_taxe(self, entreprise_id: int, taxe_id: str, data: TaxeUpdate):
        taxe = self.repo.get_by_id(taxe_id, entreprise_id)
        if not taxe:
            raise HTTPException(status_code=404, detail="Taxe introuvable")
        return self.repo.update(taxe, data.model_dump(exclude_none=True))

    def delete_taxe(self, entreprise_id: int, taxe_id: str):
        taxe = self.repo.get_by_id(taxe_id, entreprise_id)
        if not taxe:
            raise HTTPException(status_code=404, detail="Taxe introuvable")
        self.repo.delete(taxe)

    # ── Groupes ────────────────────────────────────────────
    def list_groupes(self, entreprise_id: int):
        groupes = self.repo.get_all_groupes(entreprise_id)
        # Ajoute le taux_total calculé
        for g in groupes:
            g.taux_total = sum(t.taux for t in g.taxes)
        return groupes

    def create_groupe(self, entreprise_id: int, data: GroupeTaxeCreate):
        taxes = self.repo.get_taxes_by_ids(
            [str(tid) for tid in data.taxe_ids], entreprise_id
        )
        if len(taxes) != len(data.taxe_ids):
            raise HTTPException(
                status_code=400,
                detail="Une ou plusieurs taxes sont introuvables"
            )
        groupe = self.repo.create_groupe(
            entreprise_id = entreprise_id,
            nom           = data.nom,
            description   = data.description,
            taxes         = taxes,
        )
        groupe.taux_total = sum(t.taux for t in groupe.taxes)
        return groupe

    def update_groupe(self, entreprise_id: int, groupe_id: str, data: GroupeTaxeUpdate):
        groupe = self.repo.get_groupe_by_id(groupe_id, entreprise_id)
        if not groupe:
            raise HTTPException(status_code=404, detail="Groupe introuvable")

        taxes = None
        if data.taxe_ids:
            taxes = self.repo.get_taxes_by_ids(
                [str(tid) for tid in data.taxe_ids], entreprise_id
            )

        updated = self.repo.update_groupe(
            groupe,
            data.model_dump(exclude_none=True, exclude={"taxe_ids"}),
            taxes,
        )
        updated.taux_total = sum(t.taux for t in updated.taxes)
        return updated

    def delete_groupe(self, entreprise_id: int, groupe_id: str):
        groupe = self.repo.get_groupe_by_id(groupe_id, entreprise_id)
        if not groupe:
            raise HTTPException(status_code=404, detail="Groupe introuvable")
        self.repo.delete_groupe(groupe)