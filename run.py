#!/usr/bin/env python3
"""
Production-ready server startup script.

This script starts the FastAPI application using Uvicorn with all
configuration loaded from environment variables (via .env file).

Usage:
    python run.py                    # Start with settings from .env
    DEBUG=true python run.py         # Override settings via env vars
    python run.py                    # Or use make dev/prod shortcuts

Environment Configuration:
    All settings are loaded from .env file via pydantic-settings.
    See .env.example for available options.

Note:
    - In development (reload=true), server_workers is forced to 1
    - In production (reload=false), uses server_workers from config
    - Job workers are independent and run in each process
"""

import uvicorn

from app.config import get_settings


def main() -> None:
    """Start the FastAPI application with Uvicorn."""
    settings = get_settings()

    # Force single worker in reload mode (Uvicorn limitation)
    workers = 1 if settings.reload else settings.server_workers

    if settings.reload and settings.server_workers > 1:
        print(
            f"[!] Note: reload=true, ignoring server_workers={settings.server_workers}, using 1 worker"
        )

    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"Debug mode: {settings.debug}")
    print(f"Hot reload: {settings.reload}")
    print(f"Server workers: {workers}")
    print(f"Job queue workers: {settings.job_workers} per process")
    print(f"Total job workers: {settings.job_workers * workers}")
    print()

    uvicorn.run(
        "app.main:server",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=workers,
        log_level=settings.log_level.lower(),
        access_log=settings.debug,
        # Additional production optimizations
        timeout_keep_alive=5,
        limit_concurrency=1000,
        limit_max_requests=10000,
    )


if __name__ == "__main__":
    main()
