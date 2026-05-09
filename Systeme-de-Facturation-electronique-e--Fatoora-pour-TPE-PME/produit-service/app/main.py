from fastapi import FastAPI
from app.api.routes import product_routes
from app.db.database import Base, engine

app = FastAPI(title="Product Service")

# Crée automatiquement les tables dans la base
Base.metadata.create_all(bind=engine)

# Ajoute les routes
app.include_router(product_routes.router)