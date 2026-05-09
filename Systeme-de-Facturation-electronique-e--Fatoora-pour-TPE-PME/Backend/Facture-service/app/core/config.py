from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    CLIENT_SERVICE_URL :str
    ENTREPRISE_SERVICE_URL :str
    PRODUIT_SERVICE_URL: str
    DEVIS_SERVICE_URL :str
    STOCK_SERVICE_URL: str = "http://service-stock:8003"
    MOUVEMENT_SERVICE_URL: str = "http://service-mouvement:8004"
    STOCK_DEFAULT_SOURCE_ID: int = 1
    STOCK_DEFAULT_SOURCE_TYPE: str = "DEPOT"
    STOCK_DEDUCTION_ON_STATUS: str = "VALIDEE"
    INTEGRATION_SERVICE_SECRET: str = ""
    PDF_STORAGE_DIR : str


    app_port: int = 8006
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
print(f"🔗 CLIENT_SERVICE_URL     = {settings.CLIENT_SERVICE_URL}")
print(f"🔗 ENTREPRISE_SERVICE_URL = {settings.ENTREPRISE_SERVICE_URL}")
print(f"🔗 PRODUIT_SERVICE_URL    = {settings.PRODUIT_SERVICE_URL}")
print(f"🔗 DEVIS_SERVICE_URL      = {settings.DEVIS_SERVICE_URL}")
print(f"🔗 STOCK_SERVICE_URL      = {settings.STOCK_SERVICE_URL}")
print(f"🔗 MOUVEMENT_SERVICE_URL  = {settings.MOUVEMENT_SERVICE_URL}")
