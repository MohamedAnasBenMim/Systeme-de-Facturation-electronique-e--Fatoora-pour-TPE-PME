from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.router import (
    entreprise_router,
    comptebancaire_router,
    membre_router,
    internal,
    taxe_router,
    cachet_router,
)
import os
import app.models.entreprise 
import app.models.compteBancaire 
import app.models.membre 
import app.models.taxe 
import app.models.cachet



from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Fatoora — Service Entreprise")
app.mount("/static", StaticFiles(directory="static"), name="static")



app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

os.makedirs("static/logos", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(entreprise_router.router)
app.include_router(comptebancaire_router.router)
app.include_router(membre_router.router)
app.include_router(internal.router)
app.include_router(taxe_router.router)
app.include_router(cachet_router.router)


@app.get("/health")
def health():
    return {"status": "Service Entreprise opérationnel"}