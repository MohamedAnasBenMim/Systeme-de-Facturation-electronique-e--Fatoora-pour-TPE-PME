# app/services/comptebancaire_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.comptebancaire_repository import CompteBancaireRepository
from app.schemas.comptebancaire_schema import (
    CompteBancaireCreate, CompteBancaireUpdate, CompteBancaireResponse
)


class CompteBancaireService:

    def __init__(self, db: Session):
        self.repository = CompteBancaireRepository(db)

    def create(self, data: CompteBancaireCreate, entreprise_id: int) -> CompteBancaireResponse:
        """Crée un compte bancaire lié à l'entreprise de l'utilisateur connecté."""
        compte_data = data.model_dump()
        compte_data["entreprise_id"] = entreprise_id   # forcé depuis le token, pas depuis le body
        return CompteBancaireResponse.model_validate(
            self.repository.save(compte_data)
        )

    def get_all(self, entreprise_id: int) -> list[CompteBancaireResponse]:
        """Retourne uniquement les comptes de l'entreprise connectée."""
        return [
            CompteBancaireResponse.model_validate(c)
            for c in self.repository.find_all(entreprise_id)
        ]

    def update(self, compte_id: int, data: CompteBancaireUpdate,
               entreprise_id: int) -> CompteBancaireResponse:
        """Met à jour un compte en vérifiant qu'il appartient à l'entreprise."""
        compte = self.repository.find_by_id(compte_id, entreprise_id)
        if not compte:
            raise HTTPException(status_code=404, detail="Compte introuvable")
        return CompteBancaireResponse.model_validate(
            self.repository.update(compte, data.model_dump(exclude_none=True))
        )

    def delete(self, compte_id: int, entreprise_id: int) -> None:
        """Supprime un compte en vérifiant qu'il appartient à l'entreprise."""
        compte = self.repository.find_by_id(compte_id, entreprise_id)
        if not compte:
            raise HTTPException(status_code=404, detail="Compte introuvable")
        self.repository.delete(compte)