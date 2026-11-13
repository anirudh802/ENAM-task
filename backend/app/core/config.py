import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FINN Financial Investment Agent"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DATABASE_URL: str = "sqlite:///./finn.db"

    # LLM Settings
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Web Push VAPID Settings
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_PRIVATE_KEY: Optional[str] = None
    VAPID_CLAIM_EMAIL: str = "mailto:dev@enam.local"

    # Anomaly Threshold Defaults
    DEFAULT_VOLUME_MULTIPLIER: float = 2.0
    DEFAULT_PRICE_MOVE_PCT: float = 3.5
    POLLING_INTERVAL_SECONDS: int = 300

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
