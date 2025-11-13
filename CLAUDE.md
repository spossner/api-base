# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

```bash
# Activate virtual environment (Git Bash/MINGW on Windows)
source venv/Scripts/activate

# Run in development mode (reads from .env)
make dev

# Run in debug mode with verbose logging
make debug

# Install dependencies
make install

# Clean cache files
make clean
```

## Architecture Overview

### Application Entry Points

The application uses a centralized startup system:

1. **run.py** - Main entry point that reads all configuration from `.env` via pydantic-settings
2. **app/main.py** - FastAPI application factory with lifespan management
3. Configuration is managed by **app/config.py** which uses `pydantic-settings` to load from `.env`

### Job Queue System Architecture

This application's core feature is an **asynchronous in-memory job queue** for background task processing. Understanding this system is critical:

All job queue components are organized in `app/jobs/` for better separation of concerns.

#### Components

1. **JobManager** (app/jobs/manager.py)
   - Central coordinator for job lifecycle
   - In-memory storage: `_jobs` dict stores Job objects
   - Asyncio queue: `_queue` holds job IDs for workers
   - Methods handle job submission, status updates, intermediate results, and retrieval

2. **Handler Registry** (app/jobs/handlers.py)
   - Global `HANDLERS` dict maps job types to handler functions
   - `@register_handler("job_type")` decorator for auto-registration
   - `JobContext` class passed to handlers for publishing intermediate results
   - Handlers are async functions: `async def handler(payload: dict, context: JobContext) -> dict`

3. **Background Workers** (app/jobs/worker.py)
   - Worker pool created at application startup in lifespan
   - Each worker runs `worker_loop()` - infinite loop calling `job_manager.get_next_job()` (blocking)
   - `process_job()` executes handlers with error handling
   - Graceful shutdown via task cancellation in lifespan teardown

4. **Job Schemas** (app/jobs/schemas.py)
   - Pydantic schemas for job requests and responses
   - `JobCreate`, `JobResponse`, `JobStatus`, `IntermediateResult`
   - Type definitions for API contracts

5. **Job Handlers** (app/handlers/)
   - Individual handler files register job types on import
   - Must be imported in `app/handlers/__init__.py` to register
   - Handlers can call `context.add_result(data)` multiple times during execution
   - Return value becomes `final_result` in job response

#### Data Flow

1. API endpoint receives POST /api/v1/jobs with `type` and `payload`
2. JobManager creates Job object, stores in `_jobs`, adds ID to `_queue`
3. Worker calls `get_next_job()` (blocks until job available)
4. Worker retrieves Job from `_jobs`, executes handler with JobContext
5. Handler calls `context.add_result()` throughout processing
6. Final result stored, status updated to COMPLETED/FAILED
7. Client polls GET /api/v1/jobs/{job_id} to see intermediate results and final result

#### Worker Configuration

- `JOB_WORKERS` in .env sets async workers per Uvicorn process (default 3-10)
- `SERVER_WORKERS` sets Uvicorn process workers (default 1 in dev, 4 in prod)
- Total workers = `JOB_WORKERS × SERVER_WORKERS`
- Each Uvicorn process has its own JobManager instance (not shared across processes)
- For production with multiple processes, consider external queue (Redis, RabbitMQ)

### API Structure

- API versioning: all endpoints under `/api/v1/` prefix
- **app/api/v1/router.py** - Main API router that aggregates endpoint routers
- Endpoints organized in **app/api/v1/endpoints/**:
  - items.py - CRUD example with in-memory storage
  - users.py - CRUD example with in-memory storage
  - jobs.py - Job submission and status polling
- Router hierarchy: `app.main:app` → includes `api_router` → includes endpoint routers

### Middleware & Lifecycle

- Custom middleware organized in **app/middleware/**:
  - request_logging.py - Logs requests and adds processing time headers
- Standard middleware (CORS, GZip, TrustedHost) configured in `create_application()`
- Lifespan context manager in app/main.py:
  - **Startup**: Start worker pool via `start_workers()`
  - **Shutdown**: Cancel workers via `stop_workers()`
- Swagger/ReDoc only enabled when `DEBUG=true`

### Configuration System

- Uses `pydantic-settings` with automatic `.env` loading
- All settings in `app/config.py` with type hints and defaults
- `get_settings()` uses `@lru_cache()` for singleton pattern
- Environment variables override defaults (case-insensitive)
- Key settings:
  - `DEBUG` - enables Swagger UI, verbose logging
  - `RELOAD` - hot reload (forces single Uvicorn worker)
  - `SERVER_WORKERS` - Uvicorn process workers
  - `JOB_WORKERS` - async job queue workers per process

## Adding New Features

### Adding a New Job Handler

1. Create handler file in `app/handlers/` (e.g., `my_handler.py`)
2. Import dependencies:
   ```python
   from app.jobs import JobContext, register_handler
   from typing import Any
   ```
3. Define handler with decorator:
   ```python
   @register_handler("my_job_type")
   async def my_handler(payload: dict[str, Any], context: JobContext) -> dict:
       # Access payload data
       data = payload.get("key")

       # Add intermediate results (optional, can be called multiple times)
       context.add_result({"status": "started"})

       # Do processing
       result = await process_something(data)

       # Return final result
       return {"status": "success", "result": result}
   ```
4. Import in `app/handlers/__init__.py`:
   ```python
   from app.handlers import my_handler
   ```
5. Handler is now available - submit jobs with `"type": "my_job_type"`

### Adding a New API Endpoint

1. Create endpoint file in `app/api/v1/endpoints/` or add to existing file
2. Create APIRouter and define endpoints
3. Import and include router in `app/api/v1/router.py`:
   ```python
   from app.api.v1.endpoints import my_endpoint
   api_router.include_router(my_endpoint.router, prefix="/my-resource", tags=["my-resource"])
   ```

## Development Notes

### Environment Setup

- Always activate virtual environment before running commands
- Copy `.env.example` to `.env` and adjust settings
- Use `make dev` for development, `make debug` for verbose logging
- In development: set `DEBUG=true`, `RELOAD=true`, `SERVER_WORKERS=1`
- In production: set `DEBUG=false`, `RELOAD=false`, `SERVER_WORKERS=4` (or CPU count)

### Testing the Job System

Built-in test handlers:
- `echo` - Simple echo handler for testing
- `data_processing` - Multi-step processing with progress tracking
- `long_running` - Simulates long jobs with configurable duration

Submit via:
```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{"type": "echo", "payload": {"message": "test"}}'
```

Poll status via Location header or:
```bash
curl "http://localhost:8000/api/v1/jobs/{job_id}"
```

### Logging

- Configured in `app/core/logging.py`
- Set `LOG_LEVEL` in .env (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Logs to console and `logs/app.log` (created at runtime)
- Use `logger = logging.getLogger(__name__)` in modules

### Windows-Specific Notes

- Running on Windows with Git Bash/MINGW environment
- Virtual environment activation: `source venv/Scripts/activate`
- Makefile commands work in Git Bash (uses Unix-style commands)

## Production Considerations

- Current implementation uses in-memory storage (not persistent)
- Job queue is per-process (not shared across Uvicorn workers)
- For production with multiple processes, implement:
  - Shared storage (Redis, PostgreSQL)
  - Distributed queue (Celery, RQ, Redis Queue)
- Disable Swagger UI/ReDoc (`DEBUG=false`)
- Configure proper CORS origins (not "*")
- Add authentication/authorization middleware
- Implement rate limiting
- Use reverse proxy (nginx) with HTTPS
