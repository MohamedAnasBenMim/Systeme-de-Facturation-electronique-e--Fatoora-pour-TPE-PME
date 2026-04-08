from fastapi import FastAPI
from app.models import facture, ligneFacture
from app.api.routes.facture_routes import router
from app.db.database import Base, engine  

app = FastAPI(title="facture Service")

# Crée automatiquement les tables dans la base
Base.metadata.create_all(bind=engine)

# Ajoute les routes
app.include_router(router)