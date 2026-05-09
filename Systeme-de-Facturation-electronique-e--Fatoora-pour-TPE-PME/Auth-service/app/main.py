from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine, SessionLocal
from app.routers.auth_router import router as auth_router
from app.core.seeder import seed_admin

Base.metadata.create_all(bind=engine)




app = FastAPI(
    title="Auth Service — E-Fatoora",
    description="Microservice d'authentification JWT + Bcrypt",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    seed_admin(db)
    db.close()


app.include_router(auth_router, prefix="/api")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "auth-service"}