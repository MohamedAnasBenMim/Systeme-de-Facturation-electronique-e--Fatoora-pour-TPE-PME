# app/routers/depense.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.depense import Depense, StatutDepense, CategorieDepense
from app.schemas.depense import DepenseCreate, DepenseRead
from typing import Optional
from datetime import date

router = APIRouter(prefix="/depenses", tags=["Dépenses"])

# ─── CRUD ────────────────────────────────────────────────────────────────────

@router.post("/", response_model=DepenseRead)
def creer_depense(data: DepenseCreate, entreprise_id: int, db: Session = Depends(get_db)):
    depense = Depense(**data.model_dump(), entreprise_id=entreprise_id)
    db.add(depense)
    db.commit()
    db.refresh(depense)
    return depense

@router.get("/", response_model=list[DepenseRead])
def lister_depenses(
    entreprise_id: int,
    product_id:     Optional[int]              = None,
    categorie:     Optional[CategorieDepense] = None,
    statut:        Optional[StatutDepense]    = None,
    db:            Session                    = Depends(get_db)
):
    q = db.query(Depense).filter(Depense.entreprise_id == entreprise_id)
    if product_id:  q = q.filter(Depense.product_id== product_id)
    if categorie:  q = q.filter(Depense.categorie == categorie)
    if statut:     q = q.filter(Depense.statut == statut)
    return q.all()

@router.put("/{depense_id}", response_model=DepenseRead)
def modifier_depense(depense_id: int, data: DepenseCreate, db: Session = Depends(get_db)):
    depense = db.query(Depense).filter(Depense.id == depense_id).first()
    if not depense:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    for k, v in data.model_dump().items():
        setattr(depense, k, v)
    db.commit()
    db.refresh(depense)
    return depense

@router.delete("/{depense_id}")
def supprimer_depense(depense_id: int, db: Session = Depends(get_db)):
    depense = db.query(Depense).filter(Depense.id == depense_id).first()
    if not depense:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    db.delete(depense)
    db.commit()
    return {"message": "Dépense supprimée"}

# ─── STATS POUR LE DASHBOARD ─────────────────────────────────────────────────

@router.get("/stats/global")
def stats_depenses_global(
    entreprise_id: int,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Depense).filter(Depense.entreprise_id == entreprise_id)
    if date_debut: q = q.filter(Depense.date_depense >= date_debut)
    if date_fin:   q = q.filter(Depense.date_depense <= date_fin)

    toutes = q.all()

    total_payees     = sum(d.montant for d in toutes if d.statut == StatutDepense.PAYEE)
    total_en_attente = sum(d.montant for d in toutes if d.statut == StatutDepense.EN_ATTENTE)

    par_categorie = {}
    for d in toutes:
        if d.statut != StatutDepense.ANNULEE:
            # ✅ .value pour convertir l'enum en string JSON-sérialisable
            cle = d.categorie.value if hasattr(d.categorie, "value") else str(d.categorie)
            par_categorie[cle] = par_categorie.get(cle, 0) + d.montant

    return {
        "total_depenses_payees":     round(total_payees, 3),
        "total_depenses_en_attente": round(total_en_attente, 3),
        "repartition_par_categorie": par_categorie
    }

    
@router.get("/stats/par-projet/{product_id}")
def stats_depenses_par_projet(
    product_id:     int,
    entreprise_id: int,
    db:            Session = Depends(get_db)
):
    """
    Toutes les dépenses liées à un projet/service spécifique
    """
    depenses = db.query(Depense).filter(
        Depense.entreprise_id == entreprise_id,
        Depense.product_id    == product_id,
        Depense.statut        != StatutDepense.ANNULEE
    ).all()

    total = sum(d.montant for d in depenses)
    payees = sum(d.montant for d in depenses if d.statut == StatutDepense.PAYEE)

    return {
        "product_id":        product_id,
        "total_depenses":   round(total, 3),
        "depenses_payees":  round(payees, 3),
        "nombre_depenses":  len(depenses),
        "detail":           depenses
    }