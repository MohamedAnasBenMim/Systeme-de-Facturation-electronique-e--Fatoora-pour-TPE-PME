from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost/achats_db"
    CLIENT_SERVICE_URL: str = "http://localhost:8003"
    ENTREPRISE_SERVICE_URL: str = "http://localhost:8080"
    PRODUIT_SERVICE_URL: str = "http://localhost:8004"
    AUTH_SERVICE_URL: str = "http://localhost:8001"

    class Config:
        env_file = ".env"


settings = Settings()