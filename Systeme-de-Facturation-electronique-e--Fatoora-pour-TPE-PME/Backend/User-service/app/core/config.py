from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    SECRET_KEY: str 
    INTERNAL_SECRET: str 
    ENCRYPTION_KEY: str

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    
    app_port: int = 8001
    debug: bool = True



    class Config:
        env_file = ".env"


settings = Settings()