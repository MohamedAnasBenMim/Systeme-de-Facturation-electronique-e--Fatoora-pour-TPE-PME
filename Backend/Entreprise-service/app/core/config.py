from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL            : str
    USER_SERVICE_URL        : str
    AUTH_SERVICE_URL        : str
    NOTIFICATION_SERVICE_URL: str
    SERVICE_EMAIL           : str
    SERVICE_PASSWORD        : str
    SECRET_KEY : str
    INTERNAL_SECRET: str 
    ENCRYPTION_KEY: str
    ALGORITHM : str

    class Config:
        env_file = ".env"

settings = Settings()