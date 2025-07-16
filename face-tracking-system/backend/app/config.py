import os
from pydantic import BaseSettings, ValidationError

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    class Config:
        # Loads .env from backend/.env
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        env_file_encoding = 'utf-8'

try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Environment configuration error: {e}")
