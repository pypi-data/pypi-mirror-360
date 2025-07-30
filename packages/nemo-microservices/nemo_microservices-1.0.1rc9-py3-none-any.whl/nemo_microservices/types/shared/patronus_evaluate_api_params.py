# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .patronus_evaluation_success_strategy import PatronusEvaluationSuccessStrategy

__all__ = ["PatronusEvaluateAPIParams"]


class PatronusEvaluateAPIParams(BaseModel):
    params: Optional[object] = None
    """Parameters to the Patronus Evaluate API"""

    success_strategy: Optional[PatronusEvaluationSuccessStrategy] = None
    """
    Strategy for determining whether a Patronus Evaluation API request should pass,
    especially when multiple evaluators are called in a single request. ALL_PASS
    requires all evaluators to pass for success. ANY_PASS requires only one
    evaluator to pass for success.
    """
