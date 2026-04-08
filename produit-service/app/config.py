from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    app_port: int = 8005
    debug: bool = True

    class Config:
        env_file = ".env"

# Instance globale
settings = Settings()