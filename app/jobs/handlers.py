"""Job handler registry and execution context."""

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class JobContext:
    """Context object passed to handlers for updating job state."""

    def __init__(self, job_id: str, job_manager: Any):
        """Initialize job context.

        Args:
            job_id: The unique job identifier
            job_manager: Reference to the job manager for state updates
        """
        self.job_id = job_id
        self._job_manager = job_manager

    def add_result(self, data: Any) -> None:
        """Add an intermediate result to the job.

        Args:
            data: The intermediate result data to add
        """
        self._job_manager.add_intermediate_result(self.job_id, data)
        logger.info(f"Job {self.job_id}: Added intermediate result")


JobHandler = Callable[[JobContext, dict], Any]

# Global handler registry
_handlers: dict[str, JobHandler] = {}


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

    print(f"registering handler for {job_type}")

    def decorator(func: Callable) -> Callable:
        _handlers[job_type] = func
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
    print(_handlers)
    return job_type in _handlers


def get_handler(job_type: str) -> Callable | None:
    """Get a registered handler by job type.

    Args:
        job_type: The job type identifier

    Returns:
        The handler function or None if not found
    """
    return _handlers.get(job_type)


def list_handlers() -> list[str]:
    """List all registered handler types.

    Returns:
        List of registered job type names
    """
    return list(_handlers.keys())
