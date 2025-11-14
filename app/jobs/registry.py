"""Job handler registry and execution context."""

import logging
from typing import Any, Callable

from app.jobs.base import JobContext

logger = logging.getLogger(__name__)

JobHandler = Callable[[JobContext, dict], Any]

# Global handler registry
_registry: dict[str, JobHandler] = {}


def register_handler(job_type: str) -> Callable:
    """Decorator to register a job handler for a specific job type.

    Args:
        job_type: The job type identifier

    Returns:
        Decorator function

    Example:
        @register_handler("email_send")
        async def send_email_handler(payload: dict, context: JobContext) -> dict:
            email = payload["email"]
            context.add_result({"status": "sending"})
            # ... send email ...
            return {"sent": True, "message_id": "123"}
    """

    def decorator(func: Callable) -> Callable:
        _registry[job_type] = func
        logger.info(f"Registered handler for job type: {job_type}")
        return func

    return decorator


def can_handle(job_type: str) -> bool:
    """Check if job type can be handled.
    Args:
        job_type: The job type identifier

    Returns:
        True if the job type can be handled; false otherwise
    """
    return job_type in _registry


def get_handler(job_type: str) -> Callable | None:
    """Get a registered handler by job type.

    Args:
        job_type: The job type identifier

    Returns:
        The handler function or None if not found
    """
    return _registry.get(job_type)


def list_handlers() -> list[str]:
    """List all registered handler types.

    Returns:
        List of registered job type names
    """
    return list(_registry.keys())
