# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional

from .._models import BaseModel

__all__ = ["EvaluationParams"]


class EvaluationParams(BaseModel):
    extra: Optional[object] = None
    """Any other custom parameters."""

    limit_samples: Optional[int] = None
    """Limit number of evaluation samples"""

    max_retries: Optional[int] = None
    """Maximum number of retries for failed requests."""

    max_tokens: Optional[int] = None
    """The maximum number of tokens to generate."""

    parallelism: Optional[int] = None
    """Parallelism to be used for the evaluation job.

    Typically, this represents the maximum number of concurrent requests made to the
    model.
    """

    request_timeout: Optional[int] = None
    """The timeout to be used for requests made to the model."""

    stop: Union[str, List[str], None] = None
    """Up to 4 sequences where the API will stop generating further tokens."""

    temperature: Optional[float] = None
    """Float value between 0 and 1.

    temp of 0 indicates greedy decoding, where the token with highest prob is
    chosen. Temperature can't be set to 0.0 currently.
    """

    top_p: Optional[float] = None
    """
    Float value between 0 and 1; limits to the top tokens within a certain
    probability. top_p=0 means the model will only consider the single most likely
    token for the next prediction.
    """
