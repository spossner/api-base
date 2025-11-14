"""Auto-discovery of job request types for discriminated union.

This module automatically collects all request schemas defined in handler modules
and creates a discriminated union for FastAPI endpoints.
"""

from typing import Annotated, Union

from pydantic import Field

from app.jobs.schemas import BaseJobRequest


def get_all_request_types() -> list[type[BaseJobRequest]]:
    """Discover all job request types from handler modules.

    Returns:
        List of all request type classes that inherit from BaseJobRequest
    """
    import app.handlers  # noqa: F401 - Import to trigger handler registration

    # Collect all BaseJobRequest subclasses
    request_types: list[type[BaseJobRequest]] = []

    def collect_subclasses(cls: type) -> None:
        """Recursively collect all subclasses."""
        for subclass in cls.__subclasses__():
            # Only include concrete request classes (not base classes)
            if (
                subclass.__name__ != "BaseJobRequest"
                and not subclass.__name__.startswith("_")
            ):
                request_types.append(subclass)
            collect_subclasses(subclass)

    collect_subclasses(BaseJobRequest)
    return request_types


def create_job_request_union() -> type:
    """Create a discriminated union of all job request types.

    Returns:
        Annotated union type for use in FastAPI endpoints
    """
    request_types = get_all_request_types()

    if not request_types:
        raise RuntimeError(
            "No job request types found. Did you import handler modules?"
        )

    # Create union of all request types with discriminator on 'type' field
    return Annotated[Union[tuple(request_types)], Field(discriminator="type")]


# Create the union type at module import time
JobRequest = create_job_request_union()
