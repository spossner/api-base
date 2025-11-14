"""Job-related Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Base class for all job requests
class BaseJobRequest(BaseModel):
    """Base class for all job request types."""

    type: str = Field(..., description="The type of job to execute")


class IntermediateResult(BaseModel):
    """Schema for intermediate job results."""

    timestamp: datetime
    data: Any


class JobResponse(BaseModel):
    """Schema for job status response."""

    id: str = Field(..., description="Unique job identifier")
    type: str = Field(..., description="Job type")
    status: JobStatus = Field(..., description="Current job status")
    created_at: datetime = Field(..., description="When the job was created")
    started_at: datetime | None = Field(
        None, description="When the job started executing"
    )
    completed_at: datetime | None = Field(None, description="When the job completed")
    intermediate_results: list[IntermediateResult] = Field(
        default_factory=list, description="Intermediate results during job execution"
    )
    final_result: Any | None = Field(
        None, description="Final result after job completion"
    )
    error: str | None = Field(None, description="Error message if job failed")

    class Config:
        """Pydantic config."""

        use_enum_values = True
