from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.membre_repository import MembreRepository
from app.schemas.membre_schema import (
    MembreCreate, MembreUpdate, MembreResponse
)
from app.models.membre import StatutMembre
from app.core.http_client import HttpClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MembreService:

    def __init__(self, db: Session):
        self.repo = MembreRepository(db)

    
    # INVITER
    # ─────────────────────────────────────────
    async def inviter(self, data: MembreCreate,
                      entreprise_id: int) -> MembreResponse:

        if self.repo.find_by_email(data.email, entreprise_id):
            raise HTTPException(
                status_code=400,
                detail="Cet utilisateur est déjà membre"
            )

        user_id     = None
        nom_complet = data.nom_complet

        try:
            user = await HttpClient.get(
                f"{settings.USER_SERVICE_URL}/users/by-email/{data.email}"
            )
            user_id = user["id"]
            nom_complet = nom_complet or (
                f"{user.get('prenom','')} {user.get('nom','')}".strip()
            )
            statut = StatutMembre.ACTIF
            logger.info(f"User {user_id} trouvé — ajout direct")

        except HTTPException:
            statut = StatutMembre.EN_ATTENTE
            logger.info(f"User non trouvé — invitation en attente : {data.email}")

        perms       = data.permissions
        membre_data = {
            "entreprise_id"          : entreprise_id,
            "user_id"                : user_id,
            "email"                  : data.email,
            "nom_complet"            : nom_complet,
            "poste"                  : data.poste,
            "statut"                 : statut,
            "peut_voir_devis"        : perms.peut_voir_devis,
            "peut_creer_devis"       : perms.peut_creer_devis,
            "peut_modifier_devis"    : perms.peut_modifier_devis,
            "peut_supprimer_devis"   : perms.peut_supprimer_devis,
            "peut_voir_factures"     : perms.peut_voir_factures,
            "peut_creer_factures"    : perms.peut_creer_factures,
            "peut_modifier_factures" : perms.peut_modifier_factures,
            "peut_supprimer_factures": perms.peut_supprimer_factures,
            "peut_voir_clients"      : perms.peut_voir_clients,
            "peut_creer_clients"     : perms.peut_creer_clients,
            "peut_modifier_clients"  : perms.peut_modifier_clients,
            "peut_supprimer_clients" : perms.peut_supprimer_clients,
            "peut_voir_produits"     : perms.peut_voir_produits,
            "peut_creer_produits"    : perms.peut_creer_produits,
            "peut_modifier_produits" : perms.peut_modifier_produits,
            "peut_supprimer_produits": perms.peut_supprimer_produits,
            "peut_voir_bc"           : perms.peut_voir_bc,
            "peut_creer_bc"          : perms.peut_creer_bc,
            "peut_voir_bl"           : perms.peut_voir_bl,
            "peut_creer_bl"          : perms.peut_creer_bl,
            "est_admin"              : perms.est_admin,
        }

        membre = self.repo.save(membre_data)
        await self._notifier_invitation(data.email, entreprise_id)
        return MembreResponse.from_orm_with_permissions(membre)

    
    # GET ALL
    # ─────────────────────────────────────────
    def get_all(self, entreprise_id: int) -> list[MembreResponse]:
        return [
            MembreResponse.from_orm_with_permissions(m)
            for m in self.repo.find_all(entreprise_id)
        ]
    # GET BY USER ID
    def get_by_user_id(self, user_id: int) -> MembreResponse:
        m = self.repo.find_by_user_id(user_id)
        if not m:
            raise HTTPException(
                status_code=404,
                detail="Utilisateur non membre d'une entreprise"
            )
        return MembreResponse.from_orm_with_permissions(m)

    
    # UPDATE
    def update(self, membre_id: int, data: MembreUpdate,
               entreprise_id: int) -> MembreResponse:
        m = self.repo.find_by_id(membre_id, entreprise_id)
        if not m:
            raise HTTPException(
                status_code=404, detail="Membre introuvable"
            )

        update_data = {}
        if data.poste:
            update_data["poste"] = data.poste
        if data.statut:
            update_data["statut"] = data.statut
        if data.permissions:
            p = data.permissions
            update_data.update({
                "peut_voir_devis"        : p.peut_voir_devis,
                "peut_creer_devis"       : p.peut_creer_devis,
                "peut_modifier_devis"    : p.peut_modifier_devis,
                "peut_supprimer_devis"   : p.peut_supprimer_devis,
                "peut_voir_factures"     : p.peut_voir_factures,
                "peut_creer_factures"    : p.peut_creer_factures,
                "peut_modifier_factures" : p.peut_modifier_factures,
                "peut_supprimer_factures": p.peut_supprimer_factures,
                "peut_voir_clients"      : p.peut_voir_clients,
                "peut_creer_clients"     : p.peut_creer_clients,
                "peut_modifier_clients"  : p.peut_modifier_clients,
                "peut_supprimer_clients" : p.peut_supprimer_clients,
                "peut_voir_produits"     : p.peut_voir_produits,
                "peut_creer_produits"    : p.peut_creer_produits,
                "peut_modifier_produits" : p.peut_modifier_produits,
                "peut_supprimer_produits": p.peut_supprimer_produits,
                "peut_voir_bc"           : p.peut_voir_bc,
                "peut_creer_bc"          : p.peut_creer_bc,
                "peut_voir_bl"           : p.peut_voir_bl,
                "peut_creer_bl"          : p.peut_creer_bl,
                "est_admin"              : p.est_admin,
            })

        return MembreResponse.from_orm_with_permissions(
            self.repo.update(m, update_data)
        )

 
    # ACTIVER après inscription
    def activer(self, email: str, user_id: int) -> None:
        m = self.repo.find_pending_by_email(email)
        if m:
            self.repo.activer(m, user_id)
            logger.info(f"Membre {email} activé avec user_id={user_id}")

    
    # SUPPRIMER
    def supprimer(self, membre_id: int, entreprise_id: int) -> None:
        m = self.repo.find_by_id(membre_id, entreprise_id)
        if not m:
            raise HTTPException(
                status_code=404, detail="Membre introuvable"
            )
        if m.est_admin:
            raise HTTPException(
                status_code=400,
                detail="Impossible de supprimer un administrateur"
            )
        self.repo.delete(m)

   
    # NOTIFICATION
    async def _notifier_invitation(self, email: str,
                                    entreprise_id: int) -> None:
        try:
            await HttpClient.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/",
                {
                    "message"            : "Invitation à rejoindre une entreprise",
                    "email_destinataire" : email,
                    "entreprise_id"      : entreprise_id,
                    "type"               : "INVITATION_MEMBRE"
                }
            )
        except Exception:
            pass