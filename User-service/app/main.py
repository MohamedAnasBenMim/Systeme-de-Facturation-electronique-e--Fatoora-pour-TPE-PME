from fastapi import FastAPI
from app.api.routes import user_routes
from app.api.routes import role_routes
from app.db.database import Base, engine, SessionLocal
from app.models import *
from app.core.seeder import run_seeders


app = FastAPI(title="User Service")

Base.metadata.create_all(bind=engine)

app.include_router(user_routes.router)
app.include_router(role_routes.router)
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    run_seeders(db)
    db.close()

