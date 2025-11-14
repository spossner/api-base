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

# Code Quality (using Ruff)
make format    # Auto-format code
make lint      # Lint and auto-fix issues
make check     # Format + lint (run before commit)

# Cleanup
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

1. API endpoint receives POST /api/v1/jobs with typed request (e.g., `EchoRequest`)
2. Pydantic validates request using discriminated union based on `type` field
3. JobManager creates Job object, stores in `_jobs`, adds ID to `_queue`
4. Worker calls `get_next_job()` (blocks until job available)
5. Worker retrieves Job from `_jobs`, executes handler with JobContext
6. Handler validates payload into typed request model for type safety
7. Handler calls `context.add_result()` throughout processing
8. Final result stored, status updated to COMPLETED/FAILED
9. Client polls GET /api/v1/jobs/{job_id} to see intermediate results and final result

#### Worker Configuration

- `JOB_WORKERS` in .env sets async workers per Uvicorn process (default 3-10)
- `SERVER_WORKERS` sets Uvicorn process workers (default 1 in dev, 4 in prod)
- Total workers = `JOB_WORKERS × SERVER_WORKERS`
- Each Uvicorn process has its own JobManager instance (not shared across processes)
- For production with multiple processes, consider external queue (Redis, RabbitMQ)

#### Automatic Job Cleanup

To prevent memory leaks, completed/failed jobs are automatically cleaned up:

- `JOB_RETENTION_SECONDS` - How long to keep completed jobs (default: 3600s = 1 hour)
- `JOB_CLEANUP_INTERVAL_SECONDS` - How often to run cleanup (default: 300s = 5 minutes)

Background cleanup task runs periodically and removes:
- ✅ Completed jobs older than retention period
- ✅ Failed jobs older than retention period
- ❌ Never removes pending or running jobs

**Note:** Clients should poll job results within the retention window. After cleanup, job results are no longer available.

#### Idempotency

Prevent duplicate job submissions using idempotency keys:

**Two ways to provide idempotency key:**

1. **Via Header** (recommended, industry standard):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/jobs" \
     -H "Content-Type: application/json" \
     -H "Idempotency-Key: unique-client-id-12345" \
     -d '{"type": "echo", "message": "test"}'
   ```

2. **Via Request Field**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/jobs" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "echo",
       "message": "test",
       "idempotency_key": "unique-client-id-12345"
     }'
   ```

**Behavior:**
- Same key within retention period → Returns existing job (202 response with `X-Idempotent-Replay: true` header)
- Different key or no key → Creates new job
- Key after job cleanup → Creates new job (old key is forgotten)
- Header takes precedence if both provided

**Use cases:**
- Network retries (prevent duplicate job creation)
- Client-side idempotency (same user action multiple times)
- Distributed systems (multiple servers submitting same request)

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
  - request_logging.py - Logs requests with colored output and adds processing time headers
  - utils.py - Color utilities for console logging (status/method colors)
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

The job system uses **Pydantic models** for type-safe request validation. Each handler is self-contained in its own module with both the request schema and handler function.

**Validation Features:**
- ✅ **Required fields** - Pydantic enforces all required fields
- ✅ **Type validation** - Automatic type checking with reasonable coercion
- ✅ **Field constraints** - Min/max values, regex patterns, etc.
- ✅ **No extra fields** - Rejects unexpected parameters (`extra="forbid"`)
- ✅ **Clear error messages** - Detailed validation errors returned to client

#### Structure

Create a new file `app/handlers/my_handler.py`:

```python
"""My custom job handler and request schema."""

import logging
from typing import Any, Literal

from pydantic import Field

from app.jobs import JobContext, register_handler
from app.jobs.schemas import BaseJobRequest

logger = logging.getLogger(__name__)


# ============================================================================
# Request Schema
# ============================================================================


class MyJobRequest(BaseJobRequest):
    """Request for my custom job."""

    type: Literal["my_job_type"] = "my_job_type"
    input_data: str = Field(..., description="Input data to process")
    options: dict[str, str] = Field(default_factory=dict)


# ============================================================================
# Handler
# ============================================================================


@register_handler("my_job_type")
async def my_handler(payload: dict[str, Any], context: JobContext) -> dict:
    """Process my custom job.

    Args:
        payload: Raw payload dict (will be validated into MyJobRequest)
        context: Job context for adding intermediate results

    Returns:
        Final processing result
    """
    # Validate payload into typed request
    data = MyJobRequest(**payload)

    # Type-safe access to fields
    input_data = data.input_data
    options = data.options

    # Add intermediate results (optional)
    context.add_result({"status": "started"})

    # Do processing
    result = await process_something(input_data, options)

    # Return final result
    return {"status": "success", "result": result}
```

#### Register the Handler

Import in `app/handlers/__init__.py`:

```python
from app.handlers import data_processing, echo, long_running, my_handler

__all__ = ["data_processing", "echo", "long_running", "my_handler"]
```

That's it! The request type is **automatically discovered** and added to the discriminated union. No need to manually update the union.

#### Use It

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "my_job_type",
    "input_data": "hello",
    "options": {"mode": "fast"}
  }'
```

The system automatically validates the request based on the `type` field!

### Adding a New API Endpoint

1. Create endpoint file in `app/api/v1/endpoints/` or add to existing file
2. Create APIRouter and define endpoints
3. Import and include router in `app/api/v1/router.py`:
   ```python
   from app.api.v1.endpoints import my_endpoint
   api_router.include_router(my_endpoint.router, prefix="/my-resource", tags=["my-resource"])
   ```

## Code Quality

This project uses **Ruff** for code formatting and linting.

### What is Ruff?

Ruff is an extremely fast Python linter and formatter written in Rust. It replaces Black, Flake8, isort, and more - all in one tool.

### Usage

```bash
# Format code (like Black)
make format

# Lint and auto-fix issues (like Flake8 + isort)
make lint

# Do both
make check
```

### Configuration

Simple configuration in `pyproject.toml`:
- Line length: 100 characters
- Auto-fixes import sorting, code style issues
- See `pyproject.toml` to customize rules

### PyCharm Integration

Install the **Ruff plugin** from PyCharm marketplace for automatic formatting on save.

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
  -d '{"type": "echo", "message": "test"}'
```

Poll status via Location header or:
```bash
curl "http://localhost:8000/api/v1/jobs/{job_id}"
```

### Logging

- Configured in `app/core/logging.py`
- Set `LOG_LEVEL` in .env (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Logs to console with timestamps
- Request logging includes colored status codes and processing times (via middleware)
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
