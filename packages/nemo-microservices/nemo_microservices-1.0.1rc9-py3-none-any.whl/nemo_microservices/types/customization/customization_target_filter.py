# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from ..target_status import TargetStatus

__all__ = ["CustomizationTargetFilter"]


class CustomizationTargetFilter(BaseModel):
    base_model: Optional[str] = None
    """Filter by name of the base model."""

    enabled: Optional[bool] = None
    """Filter by enabled state of models"""

    status: Optional[TargetStatus] = None
    """Normalized statuses for targets.

    - **CREATED**: The target is created, but not yet scheduled.
    - **PENDING**: The target is waiting for resource allocation.
    - **DOWNLOADING**: The target is downloading.
    - **FAILED**: The target failed to execute and terminated.
    - **READY**: The target is ready to be used.
    - **CANCELLED**: The target download was cancelled.
    - **UNKNOWN**: The target status is unknown.
    - **DELETED**: The target is deleted.
    - **DELETING**: The target is currently being deleted.
    - **DELETE_FAILED**: Failed to delete the target.
    """
