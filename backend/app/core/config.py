"""Application configuration using Pydantic settings."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "theo-cad"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    PORT: int = 8000

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/theo_cad",
        description="PostgreSQL database URL"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_MAX_CONNECTIONS: int = 50

    # Anthropic API
    ANTHROPIC_API_KEY: str = Field(
        default="",
        description="Anthropic API key for Claude"
    )
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5-20250929"
    ANTHROPIC_MAX_TOKENS: int = 4096
    ANTHROPIC_TEMPERATURE: float = 0.7

    # Security
    SECRET_KEY: str = Field(
        default="change-this-in-production",
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )

    # File Storage
    UPLOAD_DIR: str = "/tmp/theo-cad/uploads"
    OUTPUT_DIR: str = "/tmp/theo-cad/outputs"
    MAX_FILE_SIZE: int = 52428800  # 50MB

    # Celery Queue
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/1",
        description="Celery result backend URL"
    )
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600

    # Agent Configuration
    AGENT_TIMEOUT: int = 300
    MAX_CONCURRENT_AGENTS: int = 10
    AGENT_RETRY_ATTEMPTS: int = 3

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
