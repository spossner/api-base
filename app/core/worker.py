"""Background worker for processing jobs."""

import asyncio
import logging
from typing import Any

from app.core.handlers import JobContext, get_handler
from app.core.job_manager import JobManager
from app.schemas.job import JobStatus

logger = logging.getLogger(__name__)


async def process_job(job_manager: JobManager, job_id: str) -> None:
    """Process a single job.

    Args:
        job_manager: The job manager instance
        job_id: The job ID to process
    """
    job = job_manager.get_job(job_id)
    if not job:
        logger.error(f"Job {job_id} not found in storage")
        return

    logger.info(f"Processing job {job_id} (type: {job.type})")

    # Update status to running
    job_manager.update_job_status(job_id, JobStatus.RUNNING)

    try:
        # Get the handler for this job type
        handler = get_handler(job.type)
        if not handler:
            raise ValueError(f"No handler registered for job type: {job.type}")

        # Create job context
        context = JobContext(job_id, job_manager)

        # Execute the handler
        result = await handler(job.payload, context)

        # Store final result
        job_manager.set_job_result(job_id, result)
        job_manager.update_job_status(job_id, JobStatus.COMPLETED)

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        # Handle errors
        error_msg = f"{type(e).__name__}: {str(e)}"
        job_manager.set_job_error(job_id, error_msg)
        job_manager.update_job_status(job_id, JobStatus.FAILED)

        logger.exception(f"Job {job_id} failed with error: {error_msg}")


async def worker_loop(worker_id: int, job_manager: JobManager) -> None:
    """Main worker loop that continuously processes jobs.

    Args:
        worker_id: Unique identifier for this worker
        job_manager: The job manager instance
    """
    logger.info(f"Worker {worker_id} started")

    try:
        while True:
            # Get next job from queue (blocking)
            job_id = await job_manager.get_next_job()

            logger.debug(f"Worker {worker_id} picked up job {job_id}")

            # Process the job
            await process_job(job_manager, job_id)

    except asyncio.CancelledError:
        logger.info(f"Worker {worker_id} shutting down")
        raise
    except Exception as e:
        logger.exception(f"Worker {worker_id} encountered unexpected error: {e}")
        raise


async def start_workers(worker_count: int, job_manager: JobManager) -> list[asyncio.Task]:
    """Start multiple worker tasks.

    Args:
        worker_count: Number of workers to start
        job_manager: The job manager instance

    Returns:
        List of worker tasks
    """
    logger.info(f"Starting {worker_count} workers")

    workers = []
    for i in range(worker_count):
        task = asyncio.create_task(worker_loop(i, job_manager))
        workers.append(task)

    return workers


async def stop_workers(workers: list[asyncio.Task]) -> None:
    """Stop all worker tasks gracefully.

    Args:
        workers: List of worker tasks to stop
    """
    logger.info(f"Stopping {len(workers)} workers")

    # Cancel all workers
    for worker in workers:
        worker.cancel()

    # Wait for them to finish
    await asyncio.gather(*workers, return_exceptions=True)

    logger.info("All workers stopped")
