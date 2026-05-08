from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.repositories.product_repository import ProduitRepository
from app.schemas.product_schema import (
    ProduitCreate, ProduitUpdate, ProduitSearchParams,
    CategorieCreate, UniteMesureCreate, BulkUpdatePrix,
    CategorieResponse, UniteMesureResponse, ProduitResponse
)
from app.config import settings
import httpx
import csv
import io
import uuid
from datetime import datetime


class ProduitService:
    def __init__(self, db: Session):
        self.repo = ProduitRepository(db)

    # ── Catégories ─────────────────────────────────────────────────────────────
    def list_categories(self, entreprise_id: int):
        categories = self.repo.get_categories(entreprise_id)
        return [CategorieResponse.model_validate(c) for c in categories]

    def create_categorie(self, entreprise_id: int, data: CategorieCreate):
        categorie = self.repo.create_categorie(entreprise_id, data.model_dump())
        return CategorieResponse.model_validate(categorie)

    def delete_categorie(self, entreprise_id: int, categorie_id: int):
        self.repo.delete_categorie(categorie_id, entreprise_id)

    # ── Unités ─────────────────────────────────────────────────────────────────
    def list_unites(self, entreprise_id: int):
        unites = self.repo.get_unites(entreprise_id)
        return [UniteMesureResponse.model_validate(u) for u in unites]

    def create_unite(self, entreprise_id: int, data: UniteMesureCreate):
        unite = self.repo.create_unite(entreprise_id, data.model_dump())
        return UniteMesureResponse.model_validate(unite)

    # ── Calcul TTC via ms-entreprise ───────────────────────────────────────────
    async def _calculer_ttc(
        self,
        prix_ht: float,
        taxe_id: str = None,
        groupe_taxe_id: str = None,
        token: str = "",
    ) -> float:
        """Appelle ms-entreprise pour calculer le TTC exact."""
        if not taxe_id and not groupe_taxe_id:
            return prix_ht

        ids = [taxe_id] if taxe_id else []
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{settings.ENTREPRISE_SERVICE_URL}/taxes/calculer",
                    json={"ht": prix_ht, "taxe_ids": ids, "groupe_taxe_id": str(groupe_taxe_id) if groupe_taxe_id else None},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0,
                )
                if r.status_code == 200:
                    return r.json().get("ttc", prix_ht)
        except Exception:
            pass
        return prix_ht

    # ── Génération SKU automatique ─────────────────────────────────────────────
    def _generer_reference(self, designation: str, entreprise_id: int) -> str:
        # Nettoyer le préfixe (3 premières lettres de la désignation)
        prefix = designation[:3].upper().replace(" ", "").replace("-", "")
        if not prefix:
            prefix = "PRD"
        # Générer un suffixe basé sur timestamp + random pour unicité
        timestamp = datetime.now().strftime("%H%M%S")
        random_part = str(uuid.uuid4())[:4].upper()
        return f"{prefix}-{timestamp}{random_part}"

    # ── CRUD Produit ───────────────────────────────────────────────────────────
    def list(self, entreprise_id: int, params: ProduitSearchParams):
        items, total = self.repo.search(entreprise_id, params)
        return {
            "items": [ProduitResponse.model_validate(p) for p in items],
            "total": total,
            "page":  params.page,
            "pages": (total + params.limit - 1) // params.limit,
        }

    async def create(
        self, entreprise_id: int, data: ProduitCreate, token: str
    ):
        # Référence auto si non fournie
        ref = data.reference or self._generer_reference(data.designation, entreprise_id)

        if self.repo.reference_exists(ref, entreprise_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La référence '{ref}' existe déjà"
            )

        ttc = await self._calculer_ttc(
            data.prix_vente_ht,
            str(data.taxe_id) if data.taxe_id else None,
            str(data.groupe_taxe_id) if data.groupe_taxe_id else None,
            token,
        )

        payload = data.model_dump()
        payload["reference"] = ref

        produit = self.repo.create(entreprise_id, payload, ttc)
        return ProduitResponse.model_validate(produit)

    def get(self, entreprise_id: int, product_id: int):
        p = self.repo.get_by_id(product_id, entreprise_id)
        if not p:
            raise HTTPException(status_code=404, detail="Produit introuvable")
        return ProduitResponse.model_validate(p)

    def get_by_id_only(self, product_id: int):
        p = self.repo.get_by_id_simple(product_id)
        if not p:
            raise HTTPException(status_code=404, detail="Produit introuvable")
        return p

    async def update(
        self, entreprise_id: int, product_id: int, data: ProduitUpdate, token: str
    ):
        p = self.repo.get_by_id(product_id, entreprise_id)
        if not p:
            raise HTTPException(status_code=404, detail="Produit introuvable")

        if data.reference and data.reference != p.reference:
            if self.repo.reference_exists(data.reference, entreprise_id, produit_id):
                raise HTTPException(status_code=409, detail="Référence déjà utilisée")

        prix_ht = data.prix_vente_ht or p.prix_vente_ht
        taxe_id = str(data.taxe_id) if data.taxe_id else str(p.taxe_id) if p.taxe_id else None
        groupe_id = str(data.groupe_taxe_id) if data.groupe_taxe_id else str(p.groupe_taxe_id) if p.groupe_taxe_id else None

        ttc = await self._calculer_ttc(prix_ht, taxe_id, groupe_id, token)

        updated = self.repo.update(p, data.model_dump(exclude_none=True), ttc)
        return ProduitResponse.model_validate(updated)

    def delete(self, entreprise_id: int, product_id: int):
        p = self.repo.get_by_id(product_id, entreprise_id)
        if not p:
            raise HTTPException(status_code=404, detail="Produit introuvable")
        self.repo.delete(p)  # soft delete

    # Dans product_service.py, corrige upload_image :
async def upload_image(self, entreprise_id: int, product_id: int, file: UploadFile):
    p = self.repo.get_by_id(product_id, entreprise_id)
    if not p:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    if file.content_type not in ["image/png", "image/jpeg", "image/webp"]:
        raise HTTPException(status_code=400, detail="Format non supporté")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image trop volumineuse (max 5MB)")

    import os
    os.makedirs(f"static/produits/{entreprise_id}", exist_ok=True)
    extension = file.content_type.split('/')[1]
    path = f"static/produits/{entreprise_id}/{product_id}.{extension}"
    with open(path, "wb") as f:
        f.write(content)

    # URL via le gateway, pas directement le microservice
    url = f"http://localhost:{settings.app_port}/static/produits/{entreprise_id}/{product_id}.{extension}"
    updated = self.repo.update(p, {"image_url": url}, None)
    return ProduitResponse.model_validate(updated)
    
    # ── Bulk update prix ───────────────────────────────────────────────────────
    def bulk_update_prix(self, entreprise_id: int, data: BulkUpdatePrix) -> dict:
        count = self.repo.bulk_update_prix(
            entreprise_id,
            data.pourcentage,
            data.type_prix,
            str(data.categorie_id) if data.categorie_id else None,
        )
        return {"message": f"{count} produit(s) mis à jour", "count": count}

    # ── Import CSV ─────────────────────────────────────────────────────────────
    async def import_csv(
        self, entreprise_id: int, file: UploadFile, token: str
    ) -> dict:
        content = await file.read()
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        created, errors = 0, []
        colonnes_requises = {"designation", "prix_vente_ht"}

        for i, row in enumerate(reader, start=2):
            if not colonnes_requises.issubset(row.keys()):
                errors.append(f"Ligne {i}: colonnes manquantes")
                continue
            try:
                data = ProduitCreate(
                    designation   = row["designation"],
                    reference     = row.get("reference") or None,
                    code_barre    = row.get("code_barre") or None,
                    description   = row.get("description") or None,
                    marque        = row.get("marque") or None,
                    prix_achat_ht = float(row.get("prix_achat_ht", 0)),
                    prix_vente_ht = float(row["prix_vente_ht"]),
                    type          = row.get("type", "PRODUIT"),
                    is_stockable  = row.get("is_stockable", "true").lower() == "true",
                )
                await self.create(entreprise_id, data, token)
                created += 1
            except Exception as e:
                errors.append(f"Ligne {i}: {str(e)}")

        return {"created": created, "errors": errors}

    # ── Export CSV ─────────────────────────────────────────────────────────────
    def export_csv(self, entreprise_id: int) -> str:
        produits, _ = self.repo.search(entreprise_id, ProduitSearchParams(limit=10000))
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "reference", "designation", "type", "marque",
            "prix_achat_ht", "prix_vente_ht", "prix_vente_ttc",
            "is_stockable", "est_actif", "categorie",
        ])
        for p in produits:
            writer.writerow([
                p.reference, p.designation, p.type.value,
                p.marque or "",
                p.prix_achat_ht, p.prix_vente_ht, p.prix_vente_ttc or "",
                p.is_stockable, p.est_actif,
                p.categorie.nom if p.categorie else "",
            ])
        return output.getvalue()

    # Catégories 
        categories = self.repo.get_categories(entreprise_id)
        return [CategorieResponse.model_validate(c) for c in categories]

    def create_categorie(self, entreprise_id: int, data: CategorieCreate):
        categorie = self.repo.create_categorie(entreprise_id, data.model_dump())
        return CategorieResponse.model_validate(categorie)

    def delete_categorie(self, entreprise_id: int, categorie_id: int):
        if not self.repo.delete_categorie(categorie_id, entreprise_id):
            raise HTTPException(status_code=404, detail="Catégorie introuvable")

    #  Unités 
    def list_unites(self, entreprise_id: int):
        unites = self.repo.get_unites(entreprise_id)
        return [UniteMesureResponse.model_validate(u) for u in unites]

    def create_unite(self, entreprise_id: int, data: UniteMesureCreate):
        unite = self.repo.create_unite(entreprise_id, data.model_dump())
        return UniteMesureResponse.model_validate(unite)

    # ── Endpoint pour ms-stock ─────────────────────────────────────────────────
    def get_stockables(self, entreprise_id: int):
        stockables = self.repo.get_stockables(entreprise_id)
        return [ProduitResponse.model_validate(p) for p in stockables]