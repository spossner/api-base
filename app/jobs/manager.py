"""In-memory job queue manager."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from app.core.utils import create_id
from app.jobs.schemas import IntermediateResult, JobResponse, JobStatus

logger = logging.getLogger(__name__)


class Job:
    """Internal job representation."""

    def __init__(self, job_id: str, job_type: str, payload: dict[str, Any]) -> None:
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
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.intermediate_results: list[IntermediateResult] = []
        self.final_result: Any | None = None
        self.error: str | None = None

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

    def __init__(self) -> None:
        """Initialize the job manager."""
        self._jobs: dict[str, Job] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        logger.info("Job manager initialized")

    async def submit_job(self, job_type: str, payload: dict[str, Any]) -> str:
        """Submit a new job to the queue.

        Args:
            job_type: The type of job to execute
            payload: Job-specific data

        Returns:
            The unique job ID
        """
        job_id = create_id()
        job = Job(job_id, job_type, payload)

        # Store in memory
        self._jobs[job_id] = job

        # Add to queue
        await self._queue.put(job_id)

        logger.info(f"Job submitted: {job_id} (type: {job_type})")
        return job_id

    def get_job(self, job_id: str) -> Job | None:
        """Get a job by ID.

        Args:
            job_id: The job identifier

        Returns:
            The Job object or None if not found
        """
        return self._jobs.get(job_id, None)

    def get_job_response(self, job_id: str) -> JobResponse | None:
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
            intermediate = IntermediateResult(timestamp=datetime.now(), data=data)
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

    def cleanup_old_jobs(self, retention_seconds: int) -> int:
        """Remove completed/failed jobs older than retention period.

        Args:
            retention_seconds: How long to keep completed jobs (in seconds)

        Returns:
            Number of jobs removed
        """
        cutoff_time = datetime.now() - timedelta(seconds=retention_seconds)
        jobs_to_remove = []

        for job_id, job in self._jobs.items():
            # Only cleanup completed or failed jobs
            if job.status not in (JobStatus.COMPLETED, JobStatus.FAILED):
                continue

            # Check if job is old enough to remove
            if job.completed_at and job.completed_at < cutoff_time:
                jobs_to_remove.append(job_id)

        # Remove old jobs
        for job_id in jobs_to_remove:
            del self._jobs[job_id]
            logger.debug(f"Cleaned up old job: {job_id}")

        if jobs_to_remove:
            logger.info(
                f"Cleaned up {len(jobs_to_remove)} old jobs "
                f"(retention: {retention_seconds}s)"
            )

        return len(jobs_to_remove)

    def get_job_count_by_status(self, status: JobStatus) -> int:
        """Count jobs with a specific status.

        Args:
            status: Job status to count

        Returns:
            Number of jobs with the given status
        """
        return sum(1 for job in self._jobs.values() if job.status == status)


# Global job manager instance
job_manager = JobManager()
