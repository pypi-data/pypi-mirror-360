# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .patronus_evaluate_config_output import PatronusEvaluateConfigOutput

__all__ = ["PatronusRailConfigOutput"]


class PatronusRailConfigOutput(BaseModel):
    input: Optional[PatronusEvaluateConfigOutput] = None
    """Config for the Patronus Evaluate API call"""

    output: Optional[PatronusEvaluateConfigOutput] = None
    """Config for the Patronus Evaluate API call"""
