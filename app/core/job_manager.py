"""In-memory job queue manager."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from app.schemas.job import IntermediateResult, JobResponse, JobStatus

logger = logging.getLogger(__name__)


class Job:
    """Internal job representation."""

    def __init__(self, job_id: str, job_type: str, payload: dict[str, Any]):
        """Initialize a job.

        Args:
            job_id: Unique job identifier
            job_type: Type of job (handler identifier)
            payload: Job-specific data
        """
        self.id = job_id
        self.type = job_type
        self.payload = payload
        self.status = JobStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.intermediate_results: list[IntermediateResult] = []
        self.final_result: Optional[Any] = None
        self.error: Optional[str] = None

    def to_response(self) -> JobResponse:
        """Convert to response schema.

        Returns:
            JobResponse schema
        """
        return JobResponse(
            id=self.id,
            type=self.type,
            status=self.status,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            intermediate_results=self.intermediate_results,
            final_result=self.final_result,
            error=self.error,
        )


class JobManager:
    """Manages job queue and storage."""

    def __init__(self):
        """Initialize the job manager."""
        self._jobs: dict[str, Job] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        logger.info("Job manager initialized")

    async def submit_job(self, job_type: str, payload: dict[str, Any]) -> str:
        """Submit a new job to the queue.

        Args:
            job_type: The type of job to execute
            payload: Job-specific data

        Returns:
            The unique job ID
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id, job_type, payload)

        # Store in memory
        self._jobs[job_id] = job

        # Add to queue
        await self._queue.put(job_id)

        logger.info(f"Job submitted: {job_id} (type: {job_type})")
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID.

        Args:
            job_id: The job identifier

        Returns:
            The Job object or None if not found
        """
        return self._jobs.get(job_id)

    def get_job_response(self, job_id: str) -> Optional[JobResponse]:
        """Get a job response by ID.

        Args:
            job_id: The job identifier

        Returns:
            JobResponse or None if not found
        """
        job = self.get_job(job_id)
        return job.to_response() if job else None

    async def get_next_job(self) -> str:
        """Get the next job ID from the queue (blocking).

        Returns:
            The next job ID
        """
        return await self._queue.get()

    def update_job_status(self, job_id: str, status: JobStatus) -> None:
        """Update job status.

        Args:
            job_id: The job identifier
            status: New status
        """
        job = self._jobs.get(job_id)
        if job:
            job.status = status

            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now()
            elif status in (JobStatus.COMPLETED, JobStatus.FAILED):
                job.completed_at = datetime.now()

            logger.info(f"Job {job_id}: Status updated to {status}")

    def set_job_result(self, job_id: str, result: Any) -> None:
        """Set the final result for a job.

        Args:
            job_id: The job identifier
            result: The final result data
        """
        job = self._jobs.get(job_id)
        if job:
            job.final_result = result
            logger.info(f"Job {job_id}: Final result set")

    def set_job_error(self, job_id: str, error: str) -> None:
        """Set an error message for a job.

        Args:
            job_id: The job identifier
            error: The error message
        """
        job = self._jobs.get(job_id)
        if job:
            job.error = error
            logger.error(f"Job {job_id}: Error - {error}")

    def add_intermediate_result(self, job_id: str, data: Any) -> None:
        """Add an intermediate result to a job.

        Args:
            job_id: The job identifier
            data: The intermediate result data
        """
        job = self._jobs.get(job_id)
        if job:
            intermediate = IntermediateResult(
                timestamp=datetime.now(),
                data=data
            )
            job.intermediate_results.append(intermediate)
            logger.debug(f"Job {job_id}: Intermediate result added")

    def get_queue_size(self) -> int:
        """Get the current queue size.

        Returns:
            Number of jobs in queue
        """
        return self._queue.qsize()

    def get_job_count(self) -> int:
        """Get total number of jobs.

        Returns:
            Total number of jobs
        """
        return len(self._jobs)


# Global job manager instance
job_manager = JobManager()
