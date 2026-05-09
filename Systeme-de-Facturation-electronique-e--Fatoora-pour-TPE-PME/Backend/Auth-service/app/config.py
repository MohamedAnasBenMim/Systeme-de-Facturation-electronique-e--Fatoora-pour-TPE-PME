from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    SECRET_KEY: str 
    INTERNAL_SECRET: str 
    ENCRYPTION_KEY: str
    CLERK_SECRET_KEY: str
    CLERK_WEBHOOK_SECRET:str

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    
    app_port: int = 8001
    debug: bool = True


    user_service_url: str = "http://localhost:8002"
    ENTREPRISE_SERVICE_URL: str ="http://localhost:8080"

    class Config:
        env_file = ".env"


settings = Settings()