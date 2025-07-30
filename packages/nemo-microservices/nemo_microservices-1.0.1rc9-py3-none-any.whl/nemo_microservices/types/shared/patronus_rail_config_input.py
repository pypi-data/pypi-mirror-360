# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .patronus_evaluate_config_input import PatronusEvaluateConfigInput

__all__ = ["PatronusRailConfigInput"]


class PatronusRailConfigInput(BaseModel):
    input: Optional[PatronusEvaluateConfigInput] = None
    """Config for the Patronus Evaluate API call"""

    output: Optional[PatronusEvaluateConfigInput] = None
    """Config for the Patronus Evaluate API call"""
