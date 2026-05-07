from fastapi import FastAPI
from app.models import facture, ligneFacture
from app.api.routes.facture_routes import router
from app.db.database import Base, engine  
from app.core.seed_facture import seed as seed_factures


app = FastAPI(title="facture Service")

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup():
    seed_factures()

# Ajoute les routes
app.include_router(router)