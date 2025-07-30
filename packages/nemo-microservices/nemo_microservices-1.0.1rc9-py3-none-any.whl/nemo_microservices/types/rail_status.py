# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel
from .status_enum import StatusEnum

__all__ = ["RailStatus"]


class RailStatus(BaseModel):
    status: StatusEnum
    """Status of the individual rail."""
