import importlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.logging import logger, setup_logging
from app.jobs import job_manager, start_workers, stop_workers, list_handlers
from app.jobs.cleanup import start_cleanup_task, stop_cleanup_task
from app.middleware.request_logging import RequestLoggingMiddleware

# Import handlers to register them
importlib.import_module("app.handlers")

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")

    workers = None
    cleanup_task = None

    if settings.job_workers > 0:
        handlers = list_handlers()
        if len(handlers) == 0:
            logger.info("no registered handlers")
        else:
            logger.info(f"Registered handlers: {handlers}")

            # Start background workers
            workers = await start_workers(settings.job_workers, job_manager)

            # Start cleanup task
            cleanup_task = await start_cleanup_task(
                job_manager,
                settings.job_retention_seconds,
                settings.job_cleanup_interval_seconds,
            )

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")

    if cleanup_task is not None:
        await stop_cleanup_task(cleanup_task)

    if workers is not None:
        await stop_workers(workers)
        logger.info("All background workers stopped")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Middleware
    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"],
        )

    return app


server = create_application()

# main routes
server.include_router(api_router, prefix=settings.api_v1_prefix)


# health and check routes
@server.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@server.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled in production",
    }
