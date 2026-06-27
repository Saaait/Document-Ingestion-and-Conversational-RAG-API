from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: Optional[str] = None
    REDIS_URL: str
    OPENROUTER_API_KEY: str
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
