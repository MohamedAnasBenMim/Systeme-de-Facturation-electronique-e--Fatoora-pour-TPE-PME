from sqlalchemy.orm import Session
from fastapi import HTTPException
import os
from app.services.pdf_service import PdfService
from app.models.BonCommande import BonCommande, StatutBonCommande
from app.models.ligne_commande import LigneBonCommande
from app.models.ligne_devis import LigneDevis
from app.models.ligne_livraison import LigneBonLivraison
from app.models.BonLivraison import BonLivraison,StatutBonLivraison, SourceBonLivraison
from app.models.devis import Devis, StatutDevis, TypeConversionDevis
from app.services.numerotation_service import NumerotationService
from app.core.facture_client import FacturesClient
from app.schemas.bc_schema import BonCommandeCreate


class BonCommandeService:

    def __init__(self, db: Session):
        self.db         = db
        self.num_svc    = NumerotationService(db)
        self.fac_client = FacturesClient()
        self.pdf_svc    = PdfService()

    # ------------------------------------------------------------------
    # CRUD de base
    # ------------------------------------------------------------------

    def get_all(self, page: int = 1, page_size: int = 10):
        offset = (page - 1) * page_size
        total = self.db.query(BonCommande).count()
        items = self.db.query(BonCommande).offset(offset).limit(page_size).all()
        return {"total": total, "total_pages": math.ceil(total / page_size) if total > 0 else 1 , "page": page, "page_size": page_size, "items": items}

    def get_by_id(self, bc_id: int) -> BonCommande:
        bc = self.db.query(BonCommande).filter_by(id=bc_id).first()
        if not bc:
            raise HTTPException(status_code=404, detail="Bon de commande non trouvé")
        return bc

    async def create_from_devis(self, payload: BonCommandeCreate) -> BonCommande:
        """
        Crée un BC depuis un devis existant (payload.devis_id requis).
        Délègue au DevisService.convertir_en_bc pour cohérence.
        """
        if not payload.devis_id:
            raise HTTPException(status_code=400, detail="devis_id est requis pour créer un BC depuis un devis.")

        from app.services.devis_service import DevisService
        devis_svc = DevisService(self.db)
        return devis_svc.convertir_en_bc(payload.devis_id)

    async def create_manuel(self, payload: BonCommandeCreate) -> BonCommande:
       
        numero = self.num_svc.generer_numero_bc()
        bc = BonCommande(
            numero=numero,
            client_id=payload.client_id,
            statut=StatutBonCommande.BROUILLON,
            notes=payload.notes,
            date_livraison_souhaitee=payload.date_livraison_souhaitee,
        )
        self.db.add(bc)
        self.db.flush()

        for l in payload.lignes:
            montant_ht = l.quantite * l.prix_unitaire
            self.db.add(LigneBonCommande(
                bc_id=bc.id,
                product_id=l.product_id,
                description=l.description,
                quantite=l.quantite,
                prix_unitaire=l.prix_unitaire,
                taux_tva=l.taux_tva,
                montant_ht=montant_ht,
            ))

        self._recalculer_totaux(bc)
        self.db.commit()
        self.db.refresh(bc)
        return bc

    async def changer_statut(self, bc_id: int, statut: StatutBonCommande) -> BonCommande:
        bc = self.get_by_id(bc_id)
        self._valider_transition_statut(bc.statut, statut)
        bc.statut = statut
        self.db.commit()
        self.db.refresh(bc)
        return bc

    # ------------------------------------------------------------------
    # CONVERSIONS
    # ------------------------------------------------------------------

    def convertir_en_bl(self, bc_id: int) -> BonLivraison:
        """
        BC (CONFIRMÉ) → Bon de livraison.
        Toutes les lignes du BC sont copiées dans le BL.
        La quantité livrée est initialement 0 (livraison à faire).
        """
        bc = self.get_by_id(bc_id)
        self._verifier_statut_bc(bc, [StatutBonCommande.CONFIRME, StatutBonCommande.EN_COURS], "convertir en BL")

        numero_bl = self.num_svc.generer_numero_bl()
        bl = BonLivraison(
            numero=numero_bl,
            bc_id=bc.id,
            source=SourceBonLivraison.BON_COMMANDE,
            client_id=bc.client_id,
            statut=StatutBonLivraison.EN_ATTENTE,
            montant_ht=bc.montant_ht,
            montant_tva=bc.montant_tva,
            montant_ttc=bc.montant_ttc,
        )
        self.db.add(bl)
        self.db.flush()

        for l in bc.lignes:
            self.db.add(LigneBonLivraison(
                bl_id=bl.id,
                bc_ligne_id=l.id,
                product_id=l.product_id,
                description=l.description,
                quantite_commandee=l.quantite,
                quantite_livree=l.quantite,       # livraison totale prévue
                prix_unitaire=l.prix_unitaire,
                taux_tva=l.taux_tva,
                montant_ht=l.montant_ht,
            ))

        # Mettre à jour le statut BC
        bc.statut = StatutBonCommande.EN_COURS
        self.db.commit()
        self.db.refresh(bl)
        return bl

    async def convertir_en_facture(self, bc_id: int) -> dict:
        """
        BC (CONFIRMÉ) → Facture directement (sans BL).
        Cas rare mais autorisé (ex : service, prestation sans livraison physique).
        """
        bc = self.get_by_id(bc_id)
        self._verifier_statut_bc(bc, [StatutBonCommande.CONFIRME], "convertir en facture")

        numero_fac = self.num_svc.generer_numero_facture()

        payload = {
            "numero_facture": numero_fac,
            "bc_id": bc.id,
            "client_id": bc.client_id,
            "montant_ht": bc.montant_ht,
            "montant_tva": bc.montant_tva,
            "montant_ttc": bc.montant_ttc,
            "notes": bc.notes,
            "lignes": [
                {
                    "product_id": l.product_id,
                    "description": l.description,
                    "quantite": l.quantite,
                    "prix_unitaire": l.prix_unitaire,
                    "taux_tva": l.taux_tva,
                    "montant_ht": l.montant_ht,
                }
                for l in bc.lignes
            ],
        }

        facture = await self.fac_client.creer_depuis_bc(payload)

        bc.statut = StatutBonCommande.FACTURE
        self.db.commit()

        return facture

    async def generate_pdf(self, bc_id: int) -> bytes:
        bc = self.get_by_id(bc_id)
        try:
            client = await self.fac_client.get_client(bc.client_id)
        except Exception:
            client = None
        return self.pdf_svc.generer_pdf_bc(bc, client)

    # Utilitaires privés

    def _verifier_statut_bc(self, bc: BonCommande, statuts_autorises: list, action: str):
        if bc.statut not in statuts_autorises:
            autorise = ", ".join(statuts_autorises)
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de {action} : le BC est en statut '{bc.statut}' "
                       f"(requis : {autorise})."
            )

    def _valider_transition_statut(self, actuel: StatutBonCommande, nouveau: StatutBonCommande):
        """Matrice des transitions autorisées."""
        transitions = {
            StatutBonCommande.BROUILLON:  [StatutBonCommande.CONFIRME, StatutBonCommande.ANNULE],
            StatutBonCommande.CONFIRME:   [StatutBonCommande.EN_COURS, StatutBonCommande.ANNULE, StatutBonCommande.FACTURE],
            StatutBonCommande.EN_COURS:   [StatutBonCommande.LIVRE, StatutBonCommande.ANNULE],
            StatutBonCommande.LIVRE:      [StatutBonCommande.FACTURE],
            StatutBonCommande.FACTURE:    [],
            StatutBonCommande.ANNULE:     [],
        }
        if nouveau not in transitions.get(actuel, []):
            raise HTTPException(
                status_code=400,
                detail=f"Transition de statut interdite : {actuel} → {nouveau}."
            )

    def _recalculer_totaux(self, bc: BonCommande):
        ht  = sum(l.montant_ht for l in bc.lignes)
        tva = sum(l.montant_ht * (l.taux_tva / 100) for l in bc.lignes)
        bc.montant_ht  = round(ht, 2)
        bc.montant_tva = round(tva, 2)
        bc.montant_ttc = round(ht + tva, 2)