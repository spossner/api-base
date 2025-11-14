"""Long running job handler and request schema."""

import asyncio
import logging
from typing import Any, Literal

from pydantic import Field

from app.jobs import JobContext, register_handler
from app.jobs.schemas import BaseJobRequest

logger = logging.getLogger(__name__)


class LongRunningRequest(BaseJobRequest):
    """Request for long-running job."""

    type: Literal["long_running"] = "long_running"
    duration: float = Field(default=10.0, ge=0, description="Total duration in seconds")
    stages: int = Field(default=5, ge=1, description="Number of stages")


@register_handler("long_running")
async def long_running_handler(payload: dict[str, Any], context: JobContext) -> dict:
    """Simulates a long-running job with multiple stages.

    Args:
        payload: Raw payload dict (will be validated into LongRunningRequest)
        context: Job context

    Returns:
        Completion status
    """
    # Validate payload into typed request
    data = LongRunningRequest(**payload)

    duration = data.duration
    stages = data.stages
    stage_duration = duration / stages

    logger.info(f"Starting long-running job: {duration}s across {stages} stages")

    for stage in range(1, stages + 1):
        context.add_result(
            {
                "stage": stage,
                "total_stages": stages,
                "progress_percent": int((stage / stages) * 100),
                "status": "running",
            }
        )

        await asyncio.sleep(stage_duration)

    return {
        "status": "success",
        "duration": duration,
        "stages_completed": stages,
        "message": "Long-running job completed",
    }
