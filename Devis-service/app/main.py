from fastapi import FastAPI
from app.db.database import Base, engine
from app.routes import devis_routes


app = FastAPI(title="Devi_service")

Base.metadata.create_all(bind=engine)

app.include_router(devis_routes.router)