
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.numerotation import CompteurDocument


class TypeDocument:
    DEVIS    = "DEV"
    BON_COMMANDE  = "BC"
    BON_LIVRAISON = "BL"
    FACTURE  = "FAC"


class NumerotationService:

    def __init__(self, db: Session):
        self.db = db


    def generer_numero_devis(self) -> str:
        return self._generer(TypeDocument.DEVIS)

    def generer_numero_bc(self) -> str:
        return self._generer(TypeDocument.BON_COMMANDE)

    def generer_numero_bl(self) -> str:
        return self._generer(TypeDocument.BON_LIVRAISON)

    def generer_numero_facture(self) -> str:
        """
        Appelé avant d'envoyer la requête au factures-service.
        Le numéro généré ici est transmis dans le payload pour que
        la facture soit créée avec CE numéro (pas un numéro auto du microservice).
        """
        return self._generer(TypeDocument.FACTURE)

    def prochain_numero_devis(self) -> str:
        """Aperçu sans incrémenter (utile pour affichage UI)."""
        return self._apercu(TypeDocument.DEVIS)

    def prochain_numero_bc(self) -> str:
        return self._apercu(TypeDocument.BON_COMMANDE)

    def prochain_numero_bl(self) -> str:
        return self._apercu(TypeDocument.BON_LIVRAISON)

    def prochain_numero_facture(self) -> str:
        return self._apercu(TypeDocument.FACTURE)

    # ------------------------------------------------------------------
    # Implémentation interne
    # ------------------------------------------------------------------

    def _generer(self, type_doc: str) -> str:
        """
        Incrémente le compteur de façon atomique (SELECT FOR UPDATE)
        et retourne le numéro formaté.
        """
        annee = datetime.utcnow().year

        # Verrouille la ligne pour éviter les accès concurrents
        compteur = (
            self.db.execute(
                select(CompteurDocument)
                .where(
                    CompteurDocument.type_doc == type_doc,
                    CompteurDocument.annee == annee,
                )
                .with_for_update()   # <-- verrou exclusif
            )
            .scalars()
            .first()
        )

        if compteur is None:
            # Première utilisation de ce type/année : on crée le compteur
            compteur = CompteurDocument(
                type_doc=type_doc,
                annee=annee,
                dernier_numero=0,
            )
            self.db.add(compteur)
            self.db.flush()   # récupère l'id sans committer

        compteur.dernier_numero += 1
        self.db.flush()   # persiste en base (dans la transaction courante)

        return self._formater(type_doc, annee, compteur.dernier_numero)

    def _apercu(self, type_doc: str) -> str:
        """Lit sans verrouiller — résultat indicatif uniquement."""
        annee = datetime.utcnow().year
        compteur = (
            self.db.query(CompteurDocument)
            .filter_by(type_doc=type_doc, annee=annee)
            .first()
        )
        prochain = (compteur.dernier_numero + 1) if compteur else 1
        return self._formater(type_doc, annee, prochain)

    @staticmethod
    def _formater(type_doc: str, annee: int, numero: int) -> str:
        """DEV-2025-00042"""
        return f"{type_doc}-{annee}-{numero:05d}"