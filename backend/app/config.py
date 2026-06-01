import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Pydantic will automatically look for these keys in your environment/.env file
    GEMINI_API_KEY: str
    DATABASE_URL: str

    # Configuration for Pydantic v2 to load from .env file
    model_config = SettingsConfigDict(
        # This points directly to backend/.env
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate a single config instance to import across the app
settings = Settings()