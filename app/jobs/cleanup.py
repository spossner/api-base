"""Background cleanup task for old jobs."""

import asyncio
import logging

from app.jobs.manager import JobManager

logger = logging.getLogger(__name__)


async def cleanup_loop(
    job_manager: JobManager, retention_seconds: int, interval_seconds: int
) -> None:
    """Background task that periodically cleans up old jobs.

    Args:
        job_manager: The job manager instance
        retention_seconds: How long to keep completed jobs (in seconds)
        interval_seconds: How often to run cleanup (in seconds)
    """
    logger.info(
        f"Cleanup task started: retention={retention_seconds}s, interval={interval_seconds}s"
    )

    try:
        while True:
            # Wait for the cleanup interval
            await asyncio.sleep(interval_seconds)

            # Run cleanup
            removed = job_manager.cleanup_old_jobs(retention_seconds)

            # Log stats
            total_jobs = job_manager.get_job_count()
            logger.debug(
                f"Cleanup cycle: removed {removed} jobs, {total_jobs} jobs remaining"
            )

    except asyncio.CancelledError:
        logger.info("Cleanup task shutting down")
        raise
    except Exception as e:
        logger.exception(f"Cleanup task encountered error: {e}")
        raise


async def start_cleanup_task(
    job_manager: JobManager, retention_seconds: int, interval_seconds: int
) -> asyncio.Task:
    """Start the background cleanup task.

    Args:
        job_manager: The job manager instance
        retention_seconds: How long to keep completed jobs (in seconds)
        interval_seconds: How often to run cleanup (in seconds)

    Returns:
        The cleanup task
    """
    task = asyncio.create_task(
        cleanup_loop(job_manager, retention_seconds, interval_seconds)
    )
    return task


async def stop_cleanup_task(task: asyncio.Task) -> None:
    """Stop the cleanup task gracefully.

    Args:
        task: The cleanup task to stop
    """
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
