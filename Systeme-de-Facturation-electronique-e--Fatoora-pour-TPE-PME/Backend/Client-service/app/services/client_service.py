from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.client_repository import ClientRepository
from app.schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
    PotentialDuplicateResponse,
)


class ClientService:

    def __init__(self, db: Session):
        self.repo = ClientRepository(db)

    def _to_response(self, client) -> ClientResponse:
        tags = []
        if client.tags:
            tags = [t.strip().lower() for t in client.tags.split(",") if t.strip()]
        return ClientResponse(
            id=client.id,
            nom=client.nom,
            prenom=client.prenom,
            email=client.email,
            telephone=client.telephone,
            adresse=client.adresse,
            matricule_fiscal=client.matricule_fiscal,
            type_client=client.type_client,
            secteur=client.secteur,
            tags=tags,
            niveau=client.niveau,
            is_active=client.is_active,
        )

    def _check_uniqueness(self, data: ClientCreate | ClientUpdate, current_id: int | None = None):
        by_email = self.repo.get_by_email(data.email)
        if by_email and by_email.id != current_id:
            raise HTTPException(status_code=409, detail=f"Email deja utilise: {data.email}")

        if data.telephone:
            by_tel = self.repo.get_by_telephone(data.telephone)
            if by_tel and by_tel.id != current_id:
                raise HTTPException(status_code=409, detail=f"Telephone deja utilise: {data.telephone}")

        if data.matricule_fiscal:
            by_mf = self.repo.get_by_matricule_fiscal(data.matricule_fiscal)
            if by_mf and by_mf.id != current_id:
                raise HTTPException(status_code=409, detail=f"Matricule fiscal deja utilise: {data.matricule_fiscal}")

    def create_client(self, data: ClientCreate) -> ClientResponse:
        self._check_uniqueness(data)
        client = self.repo.create(data)
        return self._to_response(client)

    def get_client(self, client_id: int) -> ClientResponse:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} introuvable")
        return self._to_response(client)

    def get_all_clients(self, skip: int = 0, limit: int = 100, **filters) -> ClientListResponse:
        clients = self.repo.get_all(skip=skip, limit=limit, **filters)
        total = self.repo.count(**filters)
        return ClientListResponse(total=total, clients=[self._to_response(c) for c in clients])

    def update_client(self, client_id: int, data: ClientUpdate) -> ClientResponse:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} introuvable")

        self._check_uniqueness(data, current_id=client_id)
        updated = self.repo.update(client, data)
        return self._to_response(updated)

    def delete_client(self, client_id: int) -> None:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} introuvable")
        self.repo.delete(client)

    def get_client_by_email(self, email: str) -> ClientResponse:
        client = self.repo.get_by_email(email)
        if not client:
            raise HTTPException(status_code=404, detail=f"Client avec email '{email}' introuvable")
        return self._to_response(client)

    def potential_duplicates(self, client_id: int) -> list[PotentialDuplicateResponse]:
        base = self.repo.get_by_id(client_id)
        if not base:
            raise HTTPException(status_code=404, detail=f"Client {client_id} introuvable")

        all_clients = self.repo.get_all(skip=0, limit=10000)
        result: list[PotentialDuplicateResponse] = []

        for c in all_clients:
            if c.id == base.id:
                continue
            score = 0
            reasons = []

            if (c.email or "").lower() == (base.email or "").lower():
                score += 100
                reasons.append("email identique")
            if base.telephone and c.telephone and c.telephone == base.telephone:
                score += 80
                reasons.append("telephone identique")
            if base.matricule_fiscal and c.matricule_fiscal and c.matricule_fiscal == base.matricule_fiscal:
                score += 100
                reasons.append("matricule fiscal identique")
            if (c.nom or "").strip().lower() == (base.nom or "").strip().lower() and (c.prenom or "").strip().lower() == (base.prenom or "").strip().lower():
                score += 60
                reasons.append("nom/prenom identiques")

            if score >= 60:
                result.append(
                    PotentialDuplicateResponse(
                        client_id=c.id,
                        score=score,
                        reasons=reasons,
                        client=self._to_response(c),
                    )
                )

        return sorted(result, key=lambda x: x.score, reverse=True)
