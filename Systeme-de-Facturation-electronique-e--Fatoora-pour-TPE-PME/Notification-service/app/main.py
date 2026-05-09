from fastapi import FastAPI
from app.core.config import settings
from app.db.database import Base, engine
from app.router.notification_router import router as notification_router

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notification-service")

# Routers
app.include_router(notification_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}