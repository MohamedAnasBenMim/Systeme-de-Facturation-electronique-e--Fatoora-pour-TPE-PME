from fastapi import FastAPI
from app.db.database import Base, engine
from app.routes import devis_routes
from app.routes import bc_router
from app.routes import bl_router


app = FastAPI(title="ventes_service")

Base.metadata.create_all(bind=engine)

app.include_router(devis_routes.router)
app.include_router(bc_router.router)
app.include_router(bl_router.router)