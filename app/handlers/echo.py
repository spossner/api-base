"""Echo job handler and request schema."""

import asyncio
import logging
from typing import Any, Literal

from pydantic import Field

from app.jobs import JobContext, register_handler
from app.jobs.schemas import BaseJobRequest

logger = logging.getLogger(__name__)


class EchoRequest(BaseJobRequest):
    """Request for echo job."""

    type: Literal["echo"] = "echo"
    message: str = Field(..., description="Message to echo back")
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Optional metadata to include"
    )


@register_handler("echo")
async def echo_handler(payload: dict[str, Any], context: JobContext) -> dict:
    """Simple echo handler that returns the payload.

    This is useful for testing the job system.

    Args:
        payload: Raw payload dict (will be validated into EchoRequest)
        context: Job context

    Returns:
        The same payload with additional metadata
    """
    # Validate payload into typed request
    data = EchoRequest(**payload)

    logger.info(f"Echo handler invoked with message: {data.message}")

    context.add_result({"status": "processing", "message": "Echoing payload"})
    await asyncio.sleep(0.5)

    return {
        "status": "success",
        "message": data.message,
        "metadata": data.metadata,
        "echo_complete": True,
    }
