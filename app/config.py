from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "FastAPI Production API"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Server (Uvicorn configuration)
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    server_workers: int = 4  # Uvicorn process workers (use 1 with reload=true)

    # Job Queue
    job_workers: int = 10  # Background async job queue workers
    job_retention_seconds: int = 3600  # Keep completed jobs for 1 hour (3600s)
    job_cleanup_interval_seconds: int = 300  # Run cleanup every 5 minutes (300s)

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
