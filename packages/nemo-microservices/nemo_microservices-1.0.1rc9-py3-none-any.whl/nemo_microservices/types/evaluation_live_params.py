# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Required, TypeAlias, TypedDict

from .shared.job_status import JobStatus
from .shared_params.ownership import Ownership
from .evaluation_config_input_param import EvaluationConfigInputParam
from .evaluation_target_input_param import EvaluationTargetInputParam
from .evaluation_status_details_param import EvaluationStatusDetailsParam

__all__ = ["EvaluationLiveParams", "Config", "Target"]


class EvaluationLiveParams(TypedDict, total=False):
    config: Required[Config]
    """The evaluation configuration."""

    target: Required[Target]
    """The evaluation target."""

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    namespace: str
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    output_files_url: str
    """The place where the output files, if any, should be written."""

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The URN of the project associated with this entity."""

    result: str
    """The evaluation result URN."""

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

    status_details: EvaluationStatusDetailsParam
    """Details about the status of the evaluation."""


Config: TypeAlias = Union[str, EvaluationConfigInputParam]

Target: TypeAlias = Union[str, EvaluationTargetInputParam]
