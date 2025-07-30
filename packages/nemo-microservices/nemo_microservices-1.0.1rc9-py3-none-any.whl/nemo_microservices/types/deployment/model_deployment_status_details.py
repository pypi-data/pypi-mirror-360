# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from ..shared.job_status import JobStatus

__all__ = ["ModelDeploymentStatusDetails"]


class ModelDeploymentStatusDetails(BaseModel):
    status: JobStatus
    """Normalized statuses for all jobs.

    - **CREATED**: The job is created, but not yet scheduled.
    - **PENDING**: The job is waiting for resource allocation.
    - **RUNNING**: The job is currently running.
    - **CANCELLING**: The job is being cancelled at the user's request.
    - **CANCELLED**: The job has been cancelled by the user.
    - **CANCELLING**: The job is being cancelled at the user's request.
    - **FAILED**: The job failed to execute and terminated.
    - **COMPLETED**: The job has completed successfully.
    - **READY**: The job is ready to be used.
    - **UNKNOWN**: The job status is unknown.
    """

    description: Optional[str] = None
    """A description of the status."""
