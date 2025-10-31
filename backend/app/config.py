"""Application configuration using Pydantic Settings."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    DATABASE_URL: str = "postgresql+asyncpg://localhost/opal_safe_code"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    ENVIRONMENT: str = "development"
    PORT: Optional[int] = 8000
    LOG_LEVEL: str = "INFO"
    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic API key for Claude")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env to prevent validation errors
    )


settings = Settings()
