from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):

    app_name: str = "vente-service"
    app_env: str = "development"
    app_port: int = 8005
    debug: bool = False
    SECRET_KEY : str

    # Base de données
    database_url: str
    

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "vente.events"
    rabbitmq_prefetch_count: int = 10

    # Services externes
    auth_service_url: str = "http://auth-service:8001"
    client_service_url: str = "http://client-service:8003"
    produit_service_url: str = "http://localhost:8004"
    entreprise_service_url: str = "http://localhost:8080"
    FACTURE_SERVICE_URL: str = "http://localhost:8006"
    notification_service_url: str = "http://localhost:8007"

    # JWT
    ALGORITHM: str
   
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()