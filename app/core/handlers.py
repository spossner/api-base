"""Job handler registry and execution context."""

import logging
from datetime import datetime
from typing import Any, Callable, Protocol

logger = logging.getLogger(__name__)

# Global handler registry
HANDLERS: dict[str, Callable] = {}


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


class JobHandler(Protocol):
    """Protocol for job handlers."""

    async def __call__(self, payload: dict[str, Any], context: JobContext) -> Any:
        """Execute the job handler.

        Args:
            payload: Job-specific data
            context: Job context for updating intermediate results

        Returns:
            Final result data
        """
        ...


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
        HANDLERS[job_type] = func
        logger.info(f"Registered handler for job type: {job_type}")
        return func

    return decorator


def get_handler(job_type: str) -> Callable | None:
    """Get a registered handler by job type.

    Args:
        job_type: The job type identifier

    Returns:
        The handler function or None if not found
    """
    return HANDLERS.get(job_type)


def list_handlers() -> list[str]:
    """List all registered handler types.

    Returns:
        List of registered job type names
    """
    return list(HANDLERS.keys())
