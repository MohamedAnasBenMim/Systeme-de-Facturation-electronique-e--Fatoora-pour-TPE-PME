from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AUTH_SERVICE_URL: str
    USER_SERVICE_URL: str
    CLIENT_SERVICE_URL: str
    PRODUIT_SERVICE_URL: str
    VENTES_SERVICE_URL: str
    NOTIFICATION_SERVICE_URL: str
    FACTURE_SERVICE_URL: str
    ENTREPRISE_SERVICE_URL: str
    DEPENSES_SERVICE_URL: str
    ACHATS_SERVICE_URL: str
    STOCK_SERVICE_URL: str = "http://service-stock:8003"
    MOUVEMENT_SERVICE_URL: str = "http://service-mouvement:8004"
    INTEGRATION_SERVICE_SECRET: str = ""
    GATEWAY_PORT: int = 8000
    SECRET_KEY: str
    ALGORITHM:str


    class Config:
        env_file = ".env"

settings = Settings()
