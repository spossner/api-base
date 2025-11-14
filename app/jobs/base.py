import logging
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
