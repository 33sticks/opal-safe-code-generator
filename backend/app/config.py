"""Application configuration using Pydantic Settings."""
import json
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    DATABASE_URL: str = "postgresql+asyncpg://localhost/opal_safe_code"
    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic API key for Claude")
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    PORT: Optional[int] = 8000
    
    # Make CORS_ORIGINS optional with a good default
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if not v or v.strip() == '':
                # Empty string - use default
                return ["http://localhost:5173", "http://localhost:3000"]
            # Try to parse as JSON
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, treat as comma-separated
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env to prevent validation errors
    )


settings = Settings()
