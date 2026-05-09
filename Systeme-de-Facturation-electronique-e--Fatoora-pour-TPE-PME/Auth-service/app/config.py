from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str 
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    

    app_host: str = "0.0.0.0"
    app_port: int = 8001
    debug: bool = True

    # Compte admin initial
    admin_email: str = "admin@efatoora.com"
    admin_password: str = "Admin@2026!"

    user_service_url: str = "http://localhost:8002"

    class Config:
        env_file = ".env"


settings = Settings()