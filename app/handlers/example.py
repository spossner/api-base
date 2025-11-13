"""Example job handlers demonstrating the job system."""

import asyncio
import logging
from typing import Any

from app.jobs import JobContext, register_handler

logger = logging.getLogger(__name__)


@register_handler("data_processing")
async def process_data_handler(payload: dict[str, Any], context: JobContext) -> dict:
    """Example handler that processes data in multiple steps.

    This demonstrates how to use intermediate results to show progress.

    Args:
        payload: Expected to contain:
            - items: list of items to process
            - delay: optional delay between steps (default 1 second)
        context: Job context for adding intermediate results

    Returns:
        Final processing result
    """
    items = payload.get("items", [])
    delay = payload.get("delay", 1.0)

    logger.info(f"Starting data processing for {len(items)} items")

    # Step 1: Validation
    context.add_result({
        "step": "validation",
        "status": "started",
        "total_items": len(items)
    })
    await asyncio.sleep(delay)
    context.add_result({
        "step": "validation",
        "status": "completed",
        "valid_items": len(items)
    })

    # Step 2: Processing each item
    processed_items = []
    for i, item in enumerate(items):
        await asyncio.sleep(delay)
        processed_item = str(item).upper()
        processed_items.append(processed_item)

        # Report progress
        context.add_result({
            "step": "processing",
            "progress": f"{i + 1}/{len(items)}",
            "current_item": processed_item
        })

    # Step 3: Finalization
    context.add_result({
        "step": "finalization",
        "status": "started"
    })
    await asyncio.sleep(delay)

    # Return final result
    return {
        "status": "success",
        "total_processed": len(processed_items),
        "items": processed_items,
        "message": "All items processed successfully"
    }


@register_handler("echo")
async def echo_handler(payload: dict[str, Any], context: JobContext) -> dict:
    """Simple echo handler that returns the payload.

    This is useful for testing the job system.

    Args:
        payload: Any data to echo back
        context: Job context

    Returns:
        The same payload with additional metadata
    """
    logger.info("Echo handler invoked")

    context.add_result({"status": "processing", "message": "Echoing payload"})
    await asyncio.sleep(0.5)

    return {
        "status": "success",
        "echoed_payload": payload,
        "message": "Echo complete"
    }


@register_handler("long_running")
async def long_running_handler(payload: dict[str, Any], context: JobContext) -> dict:
    """Simulates a long-running job with multiple stages.

    Args:
        payload: Expected to contain:
            - duration: total duration in seconds (default 10)
            - stages: number of stages (default 5)
        context: Job context

    Returns:
        Completion status
    """
    duration = payload.get("duration", 10)
    stages = payload.get("stages", 5)
    stage_duration = duration / stages

    logger.info(f"Starting long-running job: {duration}s across {stages} stages")

    for stage in range(1, stages + 1):
        context.add_result({
            "stage": stage,
            "total_stages": stages,
            "progress_percent": int((stage / stages) * 100),
            "status": "running"
        })

        await asyncio.sleep(stage_duration)

    return {
        "status": "success",
        "duration": duration,
        "stages_completed": stages,
        "message": "Long-running job completed"
    }
