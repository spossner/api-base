"""Job queue framework."""

from app.jobs.handlers import JobContext, get_handler, list_handlers, register_handler
from app.jobs.manager import JobManager, job_manager
from app.jobs.schemas import IntermediateResult, JobCreate, JobResponse, JobStatus
from app.jobs.worker import start_workers, stop_workers

__all__ = [
    # Handlers
    "JobContext",
    "register_handler",
    "get_handler",
    "list_handlers",
    # Manager
    "JobManager",
    "job_manager",
    # Schemas
    "JobCreate",
    "JobResponse",
    "JobStatus",
    "IntermediateResult",
    # Workers
    "start_workers",
    "stop_workers",
]
