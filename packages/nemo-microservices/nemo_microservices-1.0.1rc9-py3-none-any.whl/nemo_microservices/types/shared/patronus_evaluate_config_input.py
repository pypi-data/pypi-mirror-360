# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .patronus_evaluate_api_params import PatronusEvaluateAPIParams

__all__ = ["PatronusEvaluateConfigInput"]


class PatronusEvaluateConfigInput(BaseModel):
    evaluate_config: Optional[PatronusEvaluateAPIParams] = None
    """Config to parameterize the Patronus Evaluate API call"""
