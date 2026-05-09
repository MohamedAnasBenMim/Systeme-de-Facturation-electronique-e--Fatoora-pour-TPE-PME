from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, func
from fastapi import HTTPException
from typing import List, Optional, Dict, Tuple
from datetime import date, datetime
from decimal import Decimal

from app.models.achat import (
    BonCommande, LigneBonCommande, Reception, LigneReception,
    BonRetour, LigneBonRetour, AvoirFournisseur, FactureFournisseur, LigneFactureFournisseur,
    LitigeFacture, AuditTrail, Fournisseur, StatutFactureFournisseur, StatutBonCommande,
    StatutReception, StatutBonRetour, StatutAvoirFournisseur
)
from app.schemas.achat_schema import (
    FournisseurCreate, FournisseurUpdate, BonCommandeCreate, ReceptionCreate, BonRetourCreate,
    FactureFournisseurCreate
)
from app.core.http_client import get_produit_by_id, get_entreprise_by_id



# ============ GESTION FOURNISSEURS ============

def create_fournisseur(db: Session, data: FournisseurCreate) -> Fournisseur:
    """Crée un nouveau fournisseur."""
    # Vérifier l'unicité de la matricule fiscale
    existing = db.query(Fournisseur).filter(Fournisseur.matricule_fiscal == data.matricule_fiscal).first()
    if existing:
        raise HTTPException(status_code=400, detail="Matricule fiscal déjà existant")
    
    try:
        fournisseur = Fournisseur(**data.dict())
        db.add(fournisseur)
        db.commit()
        db.refresh(fournisseur)
        return fournisseur
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur création fournisseur: {str(e)}")


def get_fournisseur_by_id(db: Session, fournisseur_id: int) -> Fournisseur:
    """Récupère un fournisseur par ID."""
    fournisseur = db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()
    if not fournisseur:
        raise HTTPException(status_code=404, detail=f"Fournisseur {fournisseur_id} introuvable")
    return fournisseur


def get_all_fournisseurs(db: Session, actifs_seulement: bool = True) -> List[Fournisseur]:
    """Récupère tous les fournisseurs."""
    q = db.query(Fournisseur)
    if actifs_seulement:
        q = q.filter(Fournisseur.actif == True)
    return q.all()


def update_fournisseur(db: Session, fournisseur_id: int, data: FournisseurUpdate) -> Fournisseur:
    """Met à jour un fournisseur."""
    fournisseur = get_fournisseur_by_id(db, fournisseur_id)
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(fournisseur, key, value)
    
    try:
        fournisseur.date_modification = datetime.utcnow()
        db.commit()
        db.refresh(fournisseur)
        return fournisseur
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour: {str(e)}")


# ============ BON DE COMMANDE ============

def _generer_numero_bc(db: Session, entreprise_id: int) -> str:
    """Génère un numéro BC unique."""
    count = db.query(BonCommande).filter(BonCommande.entreprise_id == entreprise_id).count()
    return f"BC-{entreprise_id}-{count + 1:06d}"


def _calculer_totaux_bc(lignes_data: List[Dict]) -> Dict:
    """Calcule les totaux d'un BC à partir des lignes."""
    total_ht = sum(l["montant_ligne"] for l in lignes_data)
    tva = round(total_ht * 0.19, 3)
    timbre_fiscal = 1.0
    total_ttc = round(total_ht + tva + timbre_fiscal, 3)
    return {
        "total_ht": round(total_ht, 3),
        "tva": tva,
        "timbre_fiscal": timbre_fiscal,
        "total_ttc": total_ttc,
    }


async def create_bon_commande(db: Session, data: BonCommandeCreate, user_id: Optional[int] = None) -> BonCommande:
    """Crée un nouveau bon de commande (en statut BROUILLON)."""
    # Vérifications
    fournisseur = get_fournisseur_by_id(db, data.fournisseur_id)
    await get_entreprise_by_id(data.entreprise_id)
    
    # Enrichir et valider les lignes
    lignes_enrichies = []
    for ligne in data.lignes:
        produit = await get_produit_by_id(ligne.product_id)
        montant = round(ligne.quantite_commandee * ligne.prix_unitaire, 3)
        
        lignes_enrichies.append({
            "product_id": ligne.product_id,
            "designation": produit.get("designation", ""),
            "reference_fournisseur": ligne.reference_fournisseur,
            "quantite_commandee": ligne.quantite_commandee,
            "quantite_receptionnable": ligne.quantite_commandee,  # Au départ = quantité commandée
            "prix_unitaire": ligne.prix_unitaire,
            "montant_ligne": montant,
        })
    
    totaux = _calculer_totaux_bc(lignes_enrichies)
    
    try:
        numero_bc = _generer_numero_bc(db, data.entreprise_id)
        
        bc = BonCommande(
            numero_bc=numero_bc,
            entreprise_id=data.entreprise_id,
            fournisseur_id=data.fournisseur_id,
            date_livraison_attendue=data.date_livraison_attendue,
            creer_par_user_id=user_id,
            notes=data.notes,
            **totaux
        )
        db.add(bc)
        db.flush()
        
        # Ajouter les lignes
        for l in lignes_enrichies:
            db.add(LigneBonCommande(bon_commande_id=bc.id, **l))
        
        # Audit trail
        db.add(AuditTrail(
            bon_commande_id=bc.id,
            action="CREATE",
            nouveau_statut=StatutBonCommande.BROUILLON.value,
            user_id=user_id,
            details_modification=f"Création BC {numero_bc} avec {len(lignes_enrichies)} lignes"
        ))
        
        db.commit()
        db.refresh(bc)
        return bc
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur création BC: {str(e)}")


def confirm_bon_commande(db: Session, bc_id: int, user_id: Optional[int] = None) -> BonCommande:
    """
    Confirme un bon de commande (passe de BROUILLON à CONFIRMEE).
    À partir de ce moment, le BC devient IMMUABLE.
    """
    bc = db.query(BonCommande).filter(BonCommande.id == bc_id).first()
    if not bc:
        raise HTTPException(status_code=404, detail=f"BC {bc_id} introuvable")
    
    if bc.statut != StatutBonCommande.BROUILLON:
        raise HTTPException(status_code=400, detail="Seuls les BCs en brouillon peuvent être confirmés")
    
    try:
        bc.statut = StatutBonCommande.CONFIRMEE
        bc.confirmee = True
        bc.date_confirmation = datetime.utcnow()
        bc.confirmer_par_user_id = user_id
        
        # Audit trail
        db.add(AuditTrail(
            bon_commande_id=bc.id,
            action="CONFIRM",
            ancien_statut=StatutBonCommande.BROUILLON.value,
            nouveau_statut=StatutBonCommande.CONFIRMEE.value,
            user_id=user_id,
            details_modification="BC confirmé et verrouillé (immuable)"
        ))
        
        db.commit()
        db.refresh(bc)
        return bc
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur confirmation BC: {str(e)}")


def get_bon_commande(db: Session, bc_id: int) -> BonCommande:
    """Récupère un BC par ID."""
    bc = db.query(BonCommande).filter(BonCommande.id == bc_id).first()
    if not bc:
        raise HTTPException(status_code=404, detail="BC introuvable")
    return bc


def get_all_bons_commande(db: Session, entreprise_id: Optional[int] = None) -> List[BonCommande]:
    """Récupère tous les BCs (optionnellement filtrés par entreprise)."""
    q = db.query(BonCommande)
    if entreprise_id:
        q = q.filter(BonCommande.entreprise_id == entreprise_id)
    return q.all()


# ============ RÉCEPTION ============

def _valider_reception(db: Session, reception_create: ReceptionCreate) -> Tuple[bool, str]:
    """Valide les quantités de réception par rapport au BC."""
    bc = db.query(BonCommande).filter(BonCommande.id == reception_create.bon_commande_id).first()
    if not bc:
        return False, "BC introuvable"
    
    if not bc.confirmee:
        return False, "Impossible de réceptionner un BC non confirmé"
    
    for ligne_reception in reception_create.lignes:
        ligne_bc = db.query(LigneBonCommande).filter(LigneBonCommande.id == ligne_reception.ligne_bc_id).first()
        if not ligne_bc:
            return False, f"Ligne BC {ligne_reception.ligne_bc_id} introuvable"
        
        # RÈGLE CRITIQUE : Ne pas réceptionner plus que commandé
        quantite_deja_receptionnee = db.query(func.sum(LigneReception.quantite_receptionnee)).filter(
            LigneReception.ligne_bc_id == ligne_reception.ligne_bc_id
        ).scalar() or 0
        
        quantite_autorisee = ligne_bc.quantite_receptionnable
        if quantite_deja_receptionnee + ligne_reception.quantite_receptionnee > quantite_autorisee:
            return False, f"Réception invalide: quantité {ligne_reception.quantite_receptionnee} dépasse le maximum autorisé {quantite_autorisee - quantite_deja_receptionnee}"
    
    return True, ""


async def create_reception(db: Session, data: ReceptionCreate, user_id: Optional[int] = None) -> Reception:
    """Crée une nouvelle réception avec contrôle strict des quantités."""
    # Validation des quantités
    is_valid, error_msg = _valider_reception(db, data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    bc = db.query(BonCommande).filter(BonCommande.id == data.bon_commande_id).first()
    
    try:
        numero_reception = f"REC-{bc.entreprise_id}-{data.bon_commande_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        reception = Reception(
            numero_reception=numero_reception,
            bon_commande_id=data.bon_commande_id,
            entreprise_id=bc.entreprise_id,
            fournisseur_id=bc.fournisseur_id,
            numero_bl=data.numero_bl,
            receptionne_par_user_id=user_id,
            notes=data.notes
        )
        db.add(reception)
        db.flush()
        
        # Ajouter les lignes et mettre à jour les quantités reçues
        for ligne_rec_create in data.lignes:
            ligne_bc = db.query(LigneBonCommande).filter(
                LigneBonCommande.id == ligne_rec_create.ligne_bc_id
            ).first()
            
            db.add(LigneReception(
                reception_id=reception.id,
                ligne_bc_id=ligne_rec_create.ligne_bc_id,
                quantite_receptionnee=ligne_rec_create.quantite_receptionnee,
                quantite_conforme=ligne_rec_create.quantite_conforme,
                quantite_non_conforme=ligne_rec_create.quantite_receptionnee - ligne_rec_create.quantite_conforme,
                conformite_acceptee=ligne_rec_create.quantite_receptionnee - ligne_rec_create.quantite_conforme == 0,
                notes_conformite=ligne_rec_create.notes_conformite
            ))
            
            # Mettre à jour la quantité reçue dans la ligne BC
            ligne_bc.quantite_receptionnee += ligne_rec_create.quantite_receptionnee
        
        # Déterminer le statut de la réception
        total_cmd = sum(l.quantite_receptionnable for l in bc.lignes)
        total_rec = sum(l.quantite_receptionnee for l in reception.lignes)
        
        if total_rec == total_cmd:
            reception.statut = StatutReception.COMPLETE
            bc.statut = StatutBonCommande.LIVREE
        else:
            reception.statut = StatutReception.PARTIELLE
            bc.statut = StatutBonCommande.DIFFERENCIEE
        
        db.commit()
        db.refresh(reception)
        return reception
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur création réception: {str(e)}")


def get_reception(db: Session, reception_id: int) -> Reception:
    """Récupère une réception par ID."""
    reception = db.query(Reception).filter(Reception.id == reception_id).first()
    if not reception:
        raise HTTPException(status_code=404, detail="Réception introuvable")
    return reception


# ============ BON DE RETOUR ============

async def create_bon_retour(db: Session, data: BonRetourCreate, user_id: Optional[int] = None) -> BonRetour:
    """Crée un bon de retour pour articles non conformes."""
    reception = db.query(Reception).filter(Reception.id == data.reception_id).first()
    if not reception:
        raise HTTPException(status_code=404, detail="Réception introuvable")
    
    bc = reception.bon_commande
    
    # Calculer les totaux du retour
    lignes_retour = []
    total_ht = 0.0
    
    for ligne_br_create in data.lignes:
        ligne_bc = db.query(LigneBonCommande).filter(
            LigneBonCommande.id == ligne_br_create.ligne_bc_id
        ).first()
        if not ligne_bc:
            raise HTTPException(status_code=404, detail="Ligne BC introuvable")
        
        montant = round(ligne_br_create.quantite_retournee * ligne_br_create.prix_unitaire, 3)
        total_ht += montant
        lignes_retour.append({
            "ligne_bc": ligne_bc,
            "montant": montant,
            "data": ligne_br_create
        })
    
    tva = round(total_ht * 0.19, 3)
    total_ttc = round(total_ht + tva, 3)
    
    try:
        numero_br = f"BR-{bc.entreprise_id}-{data.reception_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        bon_retour = BonRetour(
            numero_br=numero_br,
            reception_id=data.reception_id,
            bon_commande_id=bc.id,
            entreprise_id=bc.entreprise_id,
            fournisseur_id=bc.fournisseur_id,
            motif_retour=data.motif_retour,
            total_ht_retour=total_ht,
            total_ttc_retour=total_ttc,
            cree_par_user_id=user_id,
            notes=data.notes
        )
        db.add(bon_retour)
        db.flush()
        
        # Ajouter les lignes de retour
        for item in lignes_retour:
            db.add(LigneBonRetour(
                bon_retour_id=bon_retour.id,
                ligne_bc_id=item["data"].ligne_bc_id,
                quantite_retournee=item["data"].quantite_retournee,
                prix_unitaire=item["data"].prix_unitaire,
                montant_ligne=item["montant"]
            ))
        
        db.commit()
        db.refresh(bon_retour)
        return bon_retour
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur création bon retour: {str(e)}")


def validate_bon_retour(db: Session, br_id: int, user_id: Optional[int] = None) -> AvoirFournisseur:
    """Valide un bon de retour et génère automatiquement un avoir fournisseur."""
    br = db.query(BonRetour).filter(BonRetour.id == br_id).first()
    if not br:
        raise HTTPException(status_code=404, detail="Bon retour introuvable")
    
    if br.statut != StatutBonRetour.BROUILLON:
        raise HTTPException(status_code=400, detail="Seuls les bons retour en brouillon peuvent être validés")
    
    try:
        br.statut = StatutBonRetour.VALIDEE
        br.date_validation = datetime.utcnow()
        br.valide_par_user_id = user_id
        
        # Générer automatiquement l'avoir
        numero_avoir = f"AV-{br.entreprise_id}-{br.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        avoir = AvoirFournisseur(
            numero_avoir=numero_avoir,
            bon_retour_id=br.id,
            entreprise_id=br.entreprise_id,
            fournisseur_id=br.fournisseur_id,
            montant_ht=br.total_ht_retour,
            montant_tva=round(br.total_ht_retour * 0.19, 3),
            montant_ttc=br.total_ttc_retour,
            statut=StatutAvoirFournisseur.BROUILLON,
            cree_par_user_id=user_id
        )
        db.add(avoir)
        
        # Transition le bon retour à TRAITEE
        br.statut = StatutBonRetour.TRAITEE
        
        db.commit()
        db.refresh(avoir)
        return avoir
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur validation bon retour: {str(e)}")


# ============ RAPPROCHEMENT À 3 VOIES ============

def _three_way_match(db: Session, facture: FactureFournisseur) -> Optional[LitigeFacture]:
    """
    Effectue le rapprochement à 3 voies : BC vs Réception vs Facture.
    Retourne un litige si des écarts sont détectés au-delà du seuil toléré.
    """
    if not facture.bon_commande:
        return None  # Pas de BC associée, pas de rapprochement possible
    
    bc = facture.bon_commande
    fournisseur = bc.fournisseur
    
    # Récupérer les totaux
    total_bc = bc.total_ttc
    total_facture = facture.total_ttc
    
    ecart_montant = abs(total_facture - total_bc)
    seuil_montant = total_bc * (fournisseur.seuil_tolerance_prix / 100)
    
    # Vérifier les quantités
    total_cmd = sum(l.quantite_commandee for l in bc.lignes)
    total_rec = sum(l.quantite_receptionnee for l in bc.lignes)
    total_fact = sum(l.quantite_facturee for l in facture.lignes)
    
    ecart_quantite = abs(total_fact - total_rec)
    seuil_quantite = total_rec * (fournisseur.seuil_tolerance_quantite / 100) if total_rec > 0 else 0
    
    # Créer un litige si ecarts détectés
    if ecart_montant > seuil_montant or ecart_quantite > seuil_quantite:
        details = []
        if ecart_montant > seuil_montant:
            details.append(f"Écart montant: {ecart_montant:.3f} DT (seuil: {seuil_montant:.3f} DT)")
        if ecart_quantite > seuil_quantite:
            details.append(f"Écart quantité: {ecart_quantite} unités (seuil: {seuil_quantite})")
        
        litige = LitigeFacture(
            facture_id=facture.id,
            ecart_quantite=(ecart_quantite > seuil_quantite),
            ecart_prix=False,
            ecart_montant=(ecart_montant > seuil_montant),
            details_ecart="; ".join(details),
            seuil_tolerance_depasse=True,
            montant_litige=max(ecart_montant, 0)
        )
        return litige
    
    return None


async def create_facture_fournisseur(db: Session, data: FactureFournisseurCreate, user_id: Optional[int] = None) -> FactureFournisseur:
    """Crée une facture fournisseur et effectue le rapprochement 3 voies."""
    # Vérifications
    fournisseur = get_fournisseur_by_id(db, data.fournisseur_id)
    await get_entreprise_by_id(data.entreprise_id)
    
    bc = None
    if data.bon_commande_id:
        bc = db.query(BonCommande).filter(BonCommande.id == data.bon_commande_id).first()
        if not bc:
            raise HTTPException(status_code=404, detail="BC introuvable")
    
    # Calculer les totaux
    total_ht = data.total_ht
    total_tva = data.total_tva
    total_ttc = data.total_ttc
    total_ttc_net = total_ttc  # Sera ajusté si avoirs appliqués
    
    # Validations de montants (RÈGLE : aucun montant négatif)
    if total_ht < 0 or total_tva < 0 or total_ttc < 0:
        raise HTTPException(status_code=400, detail="Les montants ne peuvent pas être négatifs")
    
    try:
        facture = FactureFournisseur(
            numero_facture=data.numero_facture,
            bon_commande_id=data.bon_commande_id,
            entreprise_id=data.entreprise_id,
            fournisseur_id=data.fournisseur_id,
            statut=StatutFactureFournisseur.EN_RAPPROCHEMENT,
            total_ht=total_ht,
            total_tva=total_tva,
            total_ttc=total_ttc,
            total_ttc_net=total_ttc_net,
            date_facture=data.date_facture,
            date_echeance=data.date_echeance,
            reference_bon_commande_fournisseur=data.reference_bon_commande_fournisseur,
            numero_bon_livraison_fournisseur=data.numero_bon_livraison_fournisseur,
            saisie_par_user_id=user_id,
            notes=data.notes
        )
        db.add(facture)
        db.flush()
        
        # Ajouter les lignes
        for ligne_create in data.lignes:
            db.add(LigneFactureFournisseur(
                facture_id=facture.id,
                product_id=ligne_create.product_id,
                designation=ligne_create.designation,
                quantite_facturee=ligne_create.quantite_facturee,
                prix_unitaire=ligne_create.prix_unitaire,
                montant_ligne=round(ligne_create.quantite_facturee * ligne_create.prix_unitaire, 3)
            ))
        
        # Effectuer le rapprochement 3 voies
        litige = _three_way_match(db, facture)
        if litige:
            facture.statut = StatutFactureFournisseur.EN_LITIGE
            db.add(litige)
        else:
            facture.statut = StatutFactureFournisseur.VALIDEE
        
        # Audit trail
        db.add(AuditTrail(
            facture_fournisseur_id=facture.id,
            action="CREATE",
            nouveau_statut=facture.statut.value,
            user_id=user_id,
            details_modification=f"Facture {data.numero_facture} créée"
        ))
        
        db.commit()
        db.refresh(facture)
        return facture
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur création facture: {str(e)}")


def get_facture_fournisseur(db: Session, facture_id: int) -> FactureFournisseur:
    """Récupère une facture fournisseur par ID."""
    facture = db.query(FactureFournisseur).filter(FactureFournisseur.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    return facture


def get_all_factures_fournisseur(db: Session, entreprise_id: Optional[int] = None) -> List[FactureFournisseur]:
    """Récupère toutes les factures fournisseur (optionnellement filtrées par entreprise)."""
    q = db.query(FactureFournisseur)
    if entreprise_id:
        q = q.filter(FactureFournisseur.entreprise_id == entreprise_id)
    return q.all()