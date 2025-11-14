"""Data processing job handler and request schema."""

import asyncio
import logging
from typing import Any, Literal

from pydantic import Field

from app.jobs import JobContext, register_handler
from app.jobs.schemas import BaseJobRequest

logger = logging.getLogger(__name__)


class DataProcessingRequest(BaseJobRequest):
    """Request for data processing job."""

    type: Literal["data_processing"] = "data_processing"
    items: list[str] = Field(..., description="List of items to process")
    delay: float = Field(
        default=1.0, ge=0, description="Delay between steps in seconds"
    )


@register_handler("data_processing")
async def process_data_handler(payload: dict[str, Any], context: JobContext) -> dict:
    """Example handler that processes data in multiple steps.

    This demonstrates how to use intermediate results to show progress.

    Args:
        payload: Raw payload dict (will be validated into DataProcessingRequest)
        context: Job context for adding intermediate results

    Returns:
        Final processing result
    """
    # Validate payload into typed request
    data = DataProcessingRequest(**payload)

    items = data.items
    delay = data.delay

    logger.info(f"Starting data processing for {len(items)} items")

    # Step 1: Validation
    context.add_result(
        {"step": "validation", "status": "started", "total_items": len(items)}
    )
    await asyncio.sleep(delay)
    context.add_result(
        {"step": "validation", "status": "completed", "valid_items": len(items)}
    )

    # Step 2: Processing each item
    processed_items = []
    for i, item in enumerate(items):
        await asyncio.sleep(delay)
        processed_item = str(item).upper()
        processed_items.append(processed_item)

        # Report progress
        context.add_result(
            {
                "step": "processing",
                "progress": f"{i + 1}/{len(items)}",
                "current_item": processed_item,
            }
        )

    # Step 3: Finalization
    context.add_result({"step": "finalization", "status": "started"})
    await asyncio.sleep(delay)

    # Return final result
    return {
        "status": "success",
        "total_processed": len(processed_items),
        "items": processed_items,
        "message": "All items processed successfully",
    }
