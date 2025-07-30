# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel
from .rail_status import RailStatus
from .status_enum import StatusEnum
from .guardrails_data_output import GuardrailsDataOutput

__all__ = ["GuardrailCheckResponse"]


class GuardrailCheckResponse(BaseModel):
    rails_status: Dict[str, RailStatus]
    """Dictionary mapping each rail to its status."""

    status: StatusEnum
    """Overall status indicating if all rails passed or if any failed."""

    guardrails_data: Optional[GuardrailsDataOutput] = None
    """Additional data related to guardrails."""
