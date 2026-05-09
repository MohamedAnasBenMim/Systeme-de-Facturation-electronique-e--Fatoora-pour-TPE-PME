from fastapi import FastAPI
from app.api.routes import product_routes
from app.db.database import Base, engine
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Product Service")

# Crée automatiquement les tables dans la base
Base.metadata.create_all(bind=engine)

os.makedirs("static/produits", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Ajoute les routes
app.include_router(product_routes.router)