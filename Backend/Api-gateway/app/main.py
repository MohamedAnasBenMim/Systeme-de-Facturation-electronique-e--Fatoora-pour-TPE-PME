from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    auth_routes,
    client_routes,
    devis_routes,
    boncommande_routes,
    bonlivraison_routes,
    facture_routes,
    user_routes,
    product_routes,
    notification_routes,
    entreprise_routes,
    comptebancaire_routes,
    dashboard_routes,
    achats_routes,
    stock_routes
)
from fastapi.openapi.utils import get_openapi


app = FastAPI(
    title="E-Fatoora API Gateway",
    description="Point d'entrée unique pour tous les microservices",
    version="1.0.0"
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi


# CORS — autorise le frontend React

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────
app.include_router(auth_routes.router,        prefix="/api/v1")
app.include_router(client_routes.router,      prefix="/api/v1")
app.include_router(devis_routes.router,       prefix="/api/v1")
app.include_router(boncommande_routes.router, prefix="/api/v1")
app.include_router(bonlivraison_routes.router,prefix="/api/v1")
app.include_router(facture_routes.router,     prefix="/api/v1")
app.include_router(user_routes.router,        prefix="/api/v1")
app.include_router(product_routes.router,     prefix="/api/v1")
app.include_router(notification_routes.router,prefix="/api/v1")
app.include_router(entreprise_routes.router,  prefix="/api/v1")
app.include_router(comptebancaire_routes.router,prefix="/api/v1")
app.include_router(dashboard_routes.router,    prefix="/api/v1")
app.include_router(achats_routes.router,      prefix="/api/v1")
app.include_router(stock_routes.router,       prefix="/api/v1")






@app.get("/health")
def health():
    return {"status": "API Gateway opérationnel"}
