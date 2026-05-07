from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import os
from app.services.pdf_service import PdfService
from app.models.BonLivraison import BonLivraison, StatutBonLivraison, SourceBonLivraison
from app.models.ligne_livraison import LigneBonLivraison
from app.schemas.bl_schema import BonLivraisonCreate
from app.models.BonCommande import BonCommande, StatutBonCommande
from app.models.devis import Devis
from app.services.numerotation_service import NumerotationService
from app.core.facture_client import FacturesClient
import math  


class BonLivraisonService:

    def __init__(self, db: Session):
        self.db         = db
        self.num_svc    = NumerotationService(db)
        self.fac_client = FacturesClient()
        self.pdf_svc    = PdfService()

    def _recalculer_totaux(self, bl: BonLivraison) -> None:
        montant_ht  = sum(l.montant_ht for l in bl.lignes)
        montant_tva = sum(round(l.montant_ht * l.taux_tva / 100, 3) for l in bl.lignes)
    
        bl.montant_ht  = round(montant_ht, 3)
        bl.montant_tva = round(montant_tva, 3)
        bl.montant_ttc = round(montant_ht + montant_tva, 3)
    
    async def create(self, payload: BonLivraisonCreate) -> BonLivraison:
    
        numero = self.num_svc.generer_numero_bl()
    
        bl = BonLivraison(
            numero=numero,
            client_id=payload.client_id,
            source=SourceBonLivraison.MANUEL,
            statut=StatutBonLivraison.EN_ATTENTE,
            date_livraison=payload.date_livraison,
            notes=payload.notes,
        )
        self.db.add(bl)
        self.db.flush()

        for l in payload.lignes:
            montant_ht = round(l.quantite * l.prix_unitaire * (1 - l.remise / 100), 3)
            self.db.add(LigneBonLivraison(
                bl_id=bl.id,
                product_id=l.product_id,
                description=l.description,
                quantite=l.quantite,
                quantite_livree=l.quantite_livree,
                prix_unitaire=l.prix_unitaire,
                taux_tva=l.taux_tva,
                montant_ht=montant_ht,
            ))

        self._recalculer_totaux(bl)
        self.db.commit()
        self.db.refresh(bl)
        return bl


    def get_all(self, page: int = 1, page_size: int = 10):
        offset = (page - 1) * page_size
        total  = self.db.query(BonLivraison).count()
        items  = self.db.query(BonLivraison).offset(offset).limit(page_size).all()
        return {"total": total,"total_pages": math.ceil(total / page_size) if total > 0 else 1 , "page": page, "page_size": page_size, "items": items}

    def get_by_id(self, bl_id: int) -> BonLivraison:
        bl = self.db.query(BonLivraison).filter_by(id=bl_id).first()
        if not bl:
            raise HTTPException(status_code=404, detail="Bon de livraison non trouvé")
        return bl

    def delete(self, bl_id: int):
        bl = self.get_by_id(bl_id)
        if bl.statut not in (StatutBonLivraison.EN_ATTENTE, StatutBonLivraison.ANNULE):
            raise HTTPException(status_code=400, detail="Seul un BL EN_ATTENTE ou ANNULÉ peut être supprimé.")
        self.db.delete(bl)
        self.db.commit()

    # ------------------------------------------------------------------
    # Création (les conversions depuis BC/Devis passent par leurs services)
    # ------------------------------------------------------------------

    async def create_from_bon_commande(self, bc_id: int, db: Session) -> BonLivraison:
        """Délègue à BonCommandeService pour cohérence."""
        from app.services.bc_service import BonCommandeService
        bc_svc = BonCommandeService(self.db)
        return bc_svc.convertir_en_bl(bc_id)

    async def create_from_devis(self, devis_id: int) -> BonLivraison:
        """Délègue à DevisService pour cohérence."""
        from app.services.devis_service import DevisService
        devis_svc = DevisService(self.db)
        return devis_svc.convertir_en_bl(devis_id)

    # ------------------------------------------------------------------
    # ACTIONS SUR LE BL
    # ------------------------------------------------------------------

    async def confirmer_livraison(self, bl_id: int) -> BonLivraison:
        """
        Confirme que la livraison est complète.
        Si le BL est issu d'un BC, met à jour les quantités livrées dans le BC.
        Si toutes les lignes BC sont livrées, passe le BC en LIVRÉ.
        """
        bl = self.get_by_id(bl_id)
        self._verifier_statut(bl, [StatutBonLivraison.EN_ATTENTE, StatutBonLivraison.EN_COURS], "confirmer")

        bl.statut = StatutBonLivraison.LIVRE
        bl.date_livraison = datetime.utcnow()

        # Mise à jour du BC source si applicable
        if bl.bc_id:
            self._mettre_a_jour_statut_bc(bl)

        self.db.commit()
        self.db.refresh(bl)
        return bl

    async def annuler(self, bl_id: int) -> BonLivraison:
        bl = self.get_by_id(bl_id)
        self._verifier_statut(
            bl,
            [StatutBonLivraison.EN_ATTENTE, StatutBonLivraison.EN_COURS],
            "annuler"
        )
        bl.statut = StatutBonLivraison.ANNULE
        self.db.commit()
        self.db.refresh(bl)
        return bl

    async def mettre_a_jour_quantites_livrees(
        self,
        bl_id: int,
        quantites: dict[int, float]   # {ligne_id: quantite_livree}
    ) -> BonLivraison:
        """
        Met à jour les quantités livrées sur les lignes du BL.
        Si certaines lignes ont une quantité livrée < commandée, le BL passe en PARTIEL.
        """
        bl = self.get_by_id(bl_id)
        self._verifier_statut(bl, [StatutBonLivraison.EN_ATTENTE, StatutBonLivraison.EN_COURS], "mettre à jour")

        for ligne in bl.lignes:
            if ligne.id in quantites:
                qte_livree = quantites[ligne.id]
                if qte_livree < 0 or qte_livree > ligne.quantite:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Quantité livrée invalide pour la ligne {ligne.id} : {qte_livree} "
                               f"(commandée : {ligne.quantite})."
                    )
                ligne.quantite_livree = qte_livree

        # Recalcul montants sur les quantités livrées réelles
        self._recalculer_totaux_livres(bl)

        # Détecter si livraison partielle
        partiel = any(l.quantite_livree < l.quantite for l in bl.lignes)
        bl.statut = StatutBonLivraison.PARTIEL if partiel else StatutBonLivraison.EN_COURS

        self.db.commit()
        self.db.refresh(bl)
        return bl

    async def creer_bl_partiel(self, bl_id: int) -> BonLivraison:
        
        bl_parent = self.get_by_id(bl_id)
        self._verifier_statut(bl_parent, [StatutBonLivraison.PARTIEL], "créer un BL partiel")

        lignes_reliquat = [
            l for l in bl_parent.lignes
            if l.quantite_livree < l.quantite
        ]
        if not lignes_reliquat:
            raise HTTPException(status_code=400, detail="Aucun reliquat à livrer sur ce BL.")

        numero_bl = self.num_svc.generer_numero_bl()
        bl_new = BonLivraison(
            numero=numero_bl,
            bc_id=bl_parent.bc_id,
            devis_id=bl_parent.devis_id,
            source=bl_parent.source,
            bl_parent_id=bl_parent.id,
            client_id=bl_parent.client_id,
            statut=StatutBonLivraison.EN_ATTENTE,
        )
        self.db.add(bl_new)
        self.db.flush()

        for l in lignes_reliquat:
            reliquat = l.quantite - l.quantite_livree
            montant_ht = reliquat * l.prix_unitaire
            self.db.add(LigneBonLivraison(
                bl_id=bl_new.id,
                bc_ligne_id=l.bc_ligne_id,
                devis_ligne_id=l.devis_ligne_id,
                product_id=l.product_id,
                description=l.description,
                quantite=reliquat,
                quantite_livree=reliquat,
                prix_unitaire=l.prix_unitaire,
                taux_tva=l.taux_tva,
                montant_ht=montant_ht,
            ))

        self._recalculer_totaux_livres(bl_new)

        # Confirmer le BL parent sur les quantités effectivement livrées
        bl_parent.statut = StatutBonLivraison.LIVRE
        bl_parent.date_livraison = datetime.utcnow()

        self.db.commit()
        self.db.refresh(bl_new)
        return bl_new

    # ------------------------------------------------------------------
    # CONVERSIONS → FACTURE
    # ------------------------------------------------------------------

    async def convertir_en_facture(self, bl_id: int) -> dict:
        """
        BL (LIVRÉ) → Facture simple (un seul BL).
        """
        bl = self.get_by_id(bl_id)
        self._verifier_statut(bl, [StatutBonLivraison.LIVRE], "convertir en facture")

        if bl.facture_id_externe:
            raise HTTPException(
                status_code=409,
                detail=f"Ce BL a déjà été facturé (facture id={bl.facture_id_externe})."
            )

        entreprise_id = self._resolve_entreprise_id(bl)

        payload = {
            "bl_id": bl.id,
            "client_id": bl.client_id,
            "entreprise_id": entreprise_id,
            "source": "BL",
            "source_id": bl.id,
            "montant_ht": bl.montant_ht,
            "montant_tva": bl.montant_tva,
            "montant_ttc": bl.montant_ttc,
            "lignes": self._lignes_to_payload(bl.lignes, bl_numero=bl.numero),
        }

        facture = await self.fac_client.creer_depuis_bl(payload)

        bl.statut = StatutBonLivraison.FACTURE
        bl.facture_id_externe = facture.get("id")
        self.db.commit()

        return facture

    async def convertir_groupe_en_facture(self, bl_ids: list[int]) -> dict:
        """
        Plusieurs BL (LIVRÉS, même client) → une Facture groupée.
        Toutes les lignes sont fusionnées dans un seul payload.
        """
        if not bl_ids:
            raise HTTPException(status_code=400, detail="Aucun BL fourni.")

        bls = [self.get_by_id(bid) for bid in bl_ids]

        # Vérifications
        for bl in bls:
            self._verifier_statut(bl, [StatutBonLivraison.LIVRE], f"facturer le BL {bl.id}")
            if bl.facture_id_externe:
                raise HTTPException(
                    status_code=409,
                    detail=f"Le BL {bl.id} (n° {bl.numero}) a déjà été facturé."
                )

        # Tous les BL doivent appartenir au même client
        client_ids = {bl.client_id for bl in bls}
        if len(client_ids) > 1:
            raise HTTPException(
                status_code=400,
                detail="Impossible de grouper des BL de clients différents dans une même facture."
            )

        entreprise_id = self._resolve_entreprise_id(bls[0])

        # Fusion des lignes
        toutes_lignes = []
        for bl in bls:
            toutes_lignes.extend(self._lignes_to_payload(bl.lignes, bl_numero=bl.numero))

        montant_ht  = round(sum(bl.montant_ht  for bl in bls), 2)
        montant_tva = round(sum(bl.montant_tva for bl in bls), 2)
        montant_ttc = round(sum(bl.montant_ttc for bl in bls), 2)

        payload = {
            "bl_ids": bl_ids,
            "client_id": next(iter(client_ids)),
            "entreprise_id": entreprise_id,
            "source": "BL_GROUPE",
            "source_id": bl_ids[0],
            "montant_ht": montant_ht,
            "montant_tva": montant_tva,
            "montant_ttc": montant_ttc,
            "lignes": toutes_lignes,
        }

        facture = await self.fac_client.creer_groupee_depuis_bls(payload)

        # Marquer tous les BL comme facturés
        for bl in bls:
            bl.statut = StatutBonLivraison.FACTURE
            bl.facture_id_externe = facture.get("id")

        self.db.commit()
        return facture

    async def generate_pdf(self, bl_id: int) -> bytes:
        bl = self.get_by_id(bl_id)
        try:
            client = await self.fac_client.get_client(bl.client_id)
        except Exception:
            client = None
        return self.pdf_svc.generer_pdf_bl(bl, client)

    # Utilitaires privés

    def _verifier_statut(self, bl: BonLivraison, statuts_autorises: list, action: str):
        if bl.statut not in statuts_autorises:
            autorise = ", ".join(statuts_autorises)
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de {action} : le BL est en statut '{bl.statut}' "
                       f"(requis : {autorise})."
            )

    def _mettre_a_jour_statut_bc(self, bl: BonLivraison):
        """Après confirmation d'un BL, vérifie si le BC associé est entièrement livré."""
        bc = self.db.query(BonCommande).filter_by(id=bl.bc_id).first()
        if not bc:
            return

        # Somme des quantités livrées sur ce BC via tous ses BL
        for ligne_bc in bc.lignes:
            total_livre = sum(
                ll.quantite_livree
                for b in bc.bons_livraison
                if b.statut == StatutBonLivraison.LIVRE
                for ll in b.lignes
                if ll.bc_ligne_id == ligne_bc.id
            )
            ligne_bc.quantite_livree = total_livre

        # Si toutes les lignes sont entièrement livrées → BC LIVRÉ
        tout_livre = all(
            l.quantite_livree >= l.quantite
            for l in bc.lignes
        )
        if tout_livre:
            bc.statut = StatutBonCommande.LIVRE

    def _recalculer_totaux_livres(self, bl: BonLivraison):
        """Recalcule les montants sur les quantités livrées réelles."""
        ht  = sum(l.quantite_livree * l.prix_unitaire for l in bl.lignes)
        tva = sum(l.quantite_livree * l.prix_unitaire * (l.taux_tva / 100) for l in bl.lignes)
        bl.montant_ht  = round(ht, 2)
        bl.montant_tva = round(tva, 2)
        bl.montant_ttc = round(ht + tva, 2)

    def _lignes_to_payload(self, lignes, bl_numero: str = None) -> list:
        return [
            {
                "product_id": l.product_id,
                "description": f"[{bl_numero}] {l.description}" if bl_numero else l.description,
                # Facture-service peut exiger un entier strict et > 0 selon la version déployée
                "quantite": max(1, int(math.ceil(l.quantite_livree))),
                "prix_unitaire": l.prix_unitaire,
                "taux_tva": l.taux_tva,
                "montant_ht": l.montant_ht,
            }
            for l in lignes
        ]

    def _resolve_entreprise_id(self, bl: BonLivraison) -> int:
        """
        Résout l'entreprise pour la facture.
        Priorité: Devis -> BC -> fallback 1.
        """
        if bl.devis_id:
            devis = self.db.query(Devis).filter_by(id=bl.devis_id).first()
            if devis and getattr(devis, "entreprise_id", None):
                return devis.entreprise_id

        if bl.bc_id:
            bc = self.db.query(BonCommande).filter_by(id=bl.bc_id).first()
            if bc and getattr(bc, "entreprise_id", None):
                return bc.entreprise_id

        return 1
