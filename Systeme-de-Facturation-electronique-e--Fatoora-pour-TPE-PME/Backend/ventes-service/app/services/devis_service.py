from sqlalchemy.orm import Session
from fastapi import HTTPException
import os
from app.services.pdf_service import PdfService

from app.models.devis import Devis, StatutDevis, TypeConversionDevis
from app.models.ligne_devis import LigneDevis
from app.models.BonCommande import BonCommande, StatutBonCommande
from app.models.ligne_commande import LigneBonCommande
from app.models.BonLivraison import BonLivraison, StatutBonLivraison, SourceBonLivraison
from app.models.ligne_livraison import LigneBonLivraison
from app.services.numerotation_service import NumerotationService
from app.core.facture_client import FacturesClient
from app.schemas.devis_schema import DevisCreate


class DevisService:

    def __init__(self, db: Session):
        self.db       = db
        self.num_svc  = NumerotationService(db)
        self.fac_client = FacturesClient()
        self.pdf_svc    = PdfService()  
    

  

    def create(self, payload: DevisCreate) -> Devis:
        numero = self.num_svc.generer_numero_devis()
        devis = Devis(
            numero=numero,
            client_id=payload.client_id,
            date_expiration=payload.date_expiration,
        )
        self.db.add(devis)
        self.db.flush()

        for l in payload.lignes:
            montant_ht = l.quantite * l.prix_unitaire
            ligne = LigneDevis(
                devis_id=devis.id,
                product_id=l.product_id,
                quantite=l.quantite,
                prix_unitaire=l.prix_unitaire,
                montant_tva=l.montant_tva,
                montant_ht=montant_ht,
            )
            self.db.add(ligne)

        self._recalculer_totaux(devis)
        self.db.commit()
        self.db.refresh(devis)
        return devis

    def get_one(self, devis_id: int) -> Devis:
        d = self.db.query(Devis).filter_by(id=devis_id).first()
        if not d:
            raise HTTPException(status_code=404, detail="Devis non trouvé")
        return d

    def get_all(self):
        return self.db.query(Devis).all()

    def delete(self, devis_id: int) -> Devis:
        d = self.get_one(devis_id)
        if d.statut not in (StatutDevis.BROUILLON, StatutDevis.REFUSE, StatutDevis.EXPIRE):
            raise HTTPException(status_code=400, detail="Seul un devis BROUILLON/REFUSÉ/EXPIRÉ peut être supprimé.")
        self.db.delete(d)
        self.db.commit()
        return d

  

    def envoyer_devis(self, devis_id: int) -> Devis:
        d = self.get_one(devis_id)
        self._verifier_statut(d, [StatutDevis.BROUILLON], "envoyer")
        d.statut = StatutDevis.ENVOYE
        self.db.commit()
        self.db.refresh(d)
        return d

    def accepter_devis(self, devis_id: int) -> Devis:
        d = self.get_one(devis_id)
        self._verifier_statut(d, [StatutDevis.ENVOYE], "accepter")
        d.statut = StatutDevis.ACCEPTE
        self.db.commit()
        self.db.refresh(d)
        return d

    def refuser_devis(self, devis_id: int) -> Devis:
        d = self.get_one(devis_id)
        self._verifier_statut(d, [StatutDevis.ENVOYE], "refuser")
        d.statut = StatutDevis.REFUSE
        self.db.commit()
        self.db.refresh(d)
        return d

    def update_statut(self, devis_id: int, statut: StatutDevis) -> Devis:
        d = self.get_one(devis_id)
        d.statut = statut
        self.db.commit()
        self.db.refresh(d)
        return d

    # CONVERSIONS
    # ------------------------------------------------------------------

    def convertir_en_bc(self, devis_id: int) -> BonCommande:
       
        devis = self.get_one(devis_id)
        self._verifier_statut(devis, [StatutDevis.ACCEPTE], "convertir en BC")
        self._verifier_non_converti(devis)

        numero_bc = self.num_svc.generer_numero_bc()
        bc = BonCommande(
            numero=numero_bc,
            devis_id=devis.id,
            client_id=devis.client_id,
            statut=StatutBonCommande.BROUILLON,
            montant_ht=devis.montant_ht,
            montant_tva=devis.montant_tva,
            montant_ttc=devis.montant_ttc,
        )
        self.db.add(bc)
        self.db.flush()

        for l in devis.lignes:
            self.db.add(LigneBonCommande(
                bc_id=bc.id,
                devis_ligne_id=l.id,
                product_id=l.product_id,
                description=l.description,
                quantite=l.quantite,
                prix_unitaire=l.prix_unitaire,
                montant_tva=l.montant_tva,
                montant_ht=l.montant_ht,
            ))

        # Marquer le devis comme converti
        devis.statut = StatutDevis.CONVERTI
        devis.type_conversion   = TypeConversionDevis.BC
        devis.id_document_cible = bc.id

        self.db.commit()
        self.db.refresh(bc)
        return bc

    def convertir_en_bl(self, devis_id: int) -> BonLivraison:
        """
        Devis (ACCEPTÉ) → Bon de livraison directement (sans passer par un BC)
        """
        devis = self.get_one(devis_id)
        self._verifier_statut(devis, [StatutDevis.ACCEPTE], "convertir en BL")
        self._verifier_non_converti(devis)

        numero_bl = self.num_svc.generer_numero_bl()
        bl = BonLivraison(
            numero=numero_bl,
            devis_id=devis.id,
            source=SourceBonLivraison.DEVIS,
            client_id=devis.client_id,
            statut=StatutBonLivraison.EN_ATTENTE,
            montant_ht=devis.montant_ht,
            montant_tva=devis.montant_tva,
            montant_ttc=devis.montant_ttc,
        )
        self.db.add(bl)
        self.db.flush()

        for l in devis.lignes:
            self.db.add(LigneBonLivraison(
                bl_id=bl.id,
                devis_ligne_id=l.id,
                product_id=l.product_id,
                description=l.description,
                quantite=l.quantite,
                quantite_livree=l.quantite,     # livraison totale prévue
                prix_unitaire=l.prix_unitaire,
                montant_tva=l.montant_tva,
                montant_ht=l.montant_ht,
            ))

        devis.statut = StatutDevis.CONVERTI
        devis.type_conversion   = TypeConversionDevis.BL
        devis.id_document_cible = bl.id

        self.db.commit()
        self.db.refresh(bl)
        return bl

    async def convertir_en_facture(self, devis_id: int) -> dict:
        """
        Devis (ACCEPTÉ) → Facture directement.
        Génère le numéro FAC ici, l'envoie au factures-service.
        """
        devis = self.get_one(devis_id)
        self._verifier_statut(devis, [StatutDevis.ACCEPTE], "convertir en facture")
        self._verifier_non_converti(devis)

        lignes = [
            {
                "product_id": l.product_id,
                "quantite": l.quantite,
                "prix_unitaire": l.prix_unitaire,
            }
            for l in devis.lignes
        ]

        devis_data = {
            "id": devis.id,
            "client_id": devis.client_id,
            "entreprise_id": 1,  
            "lignes": lignes,
        }

        payload = {
            "devis_data": devis_data,
        }

        facture = await self.fac_client.creer_depuis_devis(devis.id, payload)

        devis.statut = StatutDevis.CONVERTI
        devis.type_conversion   = TypeConversionDevis.FACTURE
        devis.id_document_cible = facture.get("id")
        self.db.commit()

        return facture

    async def generate_pdf(self, devis_id: int) -> bytes:
        devis = self.get_one(devis_id)
        try:
            client = await self.fac_client.get_client(devis.client_id)
        except Exception:
            client = None
        return self.pdf_svc.generer_pdf_devis(devis, client)

    def _verifier_statut(self, devis: Devis, statuts_autorises: list, action: str):
        if devis.statut not in statuts_autorises:
            autorise = ", ".join(statuts_autorises)
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de {action} : le devis est en statut '{devis.statut}' "
                       f"(statut requis : {autorise})."
            )

    def _verifier_non_converti(self, devis: Devis):
        if devis.statut == StatutDevis.CONVERTI:
            raise HTTPException(
                status_code=409,
                detail=f"Ce devis a déjà été converti en {devis.type_conversion} "
                       f"(id={devis.id_document_cible})."
            )

    def _recalculer_totaux(self, devis: Devis):
        ht  = sum(l.montant_ht for l in devis.lignes)
        tva = sum(l.montant_ht * (l.montant_tva / 100) for l in devis.lignes)
        devis.montant_ht  = round(ht, 2)
        devis.montant_tva = round(tva, 2)
        devis.montant_ttc = round(ht + tva, 2)