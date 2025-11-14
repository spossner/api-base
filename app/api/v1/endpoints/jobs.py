"""Job management endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from app.jobs import JobResponse, job_manager, list_handlers
from app.jobs.registry import can_handle
from app.jobs.request_union import JobRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_job(
    job_request: JobRequest,
    request: Request,
    response: Response,
    idempotency_key: Annotated[str | None, Header()] = None,
) -> JobResponse:
    """Submit a new job for asynchronous processing.

    Supports idempotency via:
    1. Header: `Idempotency-Key: <unique-key>`
    2. Request field: `idempotency_key` in request body

    Header takes precedence if both are provided.

    Accepts typed job requests with discriminated union based on 'type' field:
    - DataProcessingRequest: type="data_processing"
    - EchoRequest: type="echo"
    - LongRunningRequest: type="long_running"

    Args:
        job_request: Typed job creation request
        request: FastAPI request object (for building Location URL)
        response: FastAPI response object (for setting headers)
        idempotency_key: Optional idempotency key from header

    Returns:
        JobResponse with job details

    Raises:
        HTTPException: If job type is not registered
    """
    # Validate that handler exists for this job type
    if not can_handle(job_request.type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown job type: {job_request.type}.",
        )

    # Determine idempotency key (header takes precedence)
    final_idempotency_key = idempotency_key or job_request.idempotency_key

    # Convert typed request to dict, excluding 'type' and 'idempotency_key'
    payload = job_request.model_dump(exclude={"type", "idempotency_key"})

    # Submit job with idempotency
    job_id, is_new = await job_manager.submit_job(
        job_request.type, payload, final_idempotency_key
    )

    # Get job response
    job_response = job_manager.get_job_response(job_id)
    if not job_response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job",
        )

    # Set Location header pointing to the status endpoint
    base_url = str(request.base_url).rstrip("/")
    location = f"{base_url}/api/v1/jobs/{job_id}"
    response.headers["Location"] = location

    # Add custom header if this was an idempotent request
    if not is_new and final_idempotency_key:
        response.headers["X-Idempotent-Replay"] = "true"

    logger.info(
        f"Job {job_id} {'submitted' if is_new else 'returned (idempotent)'} "
        f"successfully, Location: {location}"
    )

    return job_response


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str) -> JobResponse:
    """Get the status and results of a job.

    Args:
        job_id: The unique job identifier

    Returns:
        JobResponse with current status, intermediate results, and final result

    Raises:
        HTTPException: If job not found
    """
    job_response = job_manager.get_job_response(job_id)

    if not job_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found"
        )

    return job_response


@router.get("/jobs", response_model=dict)
async def get_queue_info() -> dict:
    """Get information about the job queue.

    Returns:
        Dictionary with queue statistics
    """
    return {
        "total_jobs": job_manager.get_job_count(),
        "queue_size": job_manager.get_queue_size(),
        "available_job_types": list_handlers(),
    }
