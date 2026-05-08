from fastapi import FastAPI
from app.db.database import Base, engine
from app.router import depense_router
from app.core.seed_depense import seed as seed_depenses



app = FastAPI(title="Depense_service")

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup():
    seed_depenses()
    
app.include_router(depense_router.router)