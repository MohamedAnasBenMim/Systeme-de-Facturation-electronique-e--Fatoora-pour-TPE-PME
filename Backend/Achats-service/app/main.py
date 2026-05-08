from fastapi import FastAPI
from app.models.achat import (
    Fournisseur, BonCommande, LigneBonCommande, Reception, LigneReception,
    BonRetour, LigneBonRetour, AvoirFournisseur, FactureFournisseur, LigneFactureFournisseur,
    LitigeFacture, AuditTrail
)
from app.routes.achat_routes import router
from app.db.database import Base, engine
from app.core.seed_achat import seed


app = FastAPI(
    title="Achats Service")

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup():
    seed()

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "Achats Service"}