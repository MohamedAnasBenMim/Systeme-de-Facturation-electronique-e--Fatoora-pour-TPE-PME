from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.routes.client_routes import router as client_routes


# Création des tables au démarrage
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Client Microservice")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Inclusion du router
app.include_router(client_routes)


@app.get("/", tags=["Health"])
def root():
    return {"status": "running", "service": "client-microservice"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}