# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .cached_outputs_data import CachedOutputsData
from .retriever_pipeline_data_output import RetrieverPipelineDataOutput

__all__ = ["RetrieverTargetOutput"]


class RetrieverTargetOutput(BaseModel):
    cached_outputs: Optional[CachedOutputsData] = None
    """An evaluation target which contains cached outputs."""

    pipeline: Optional[RetrieverPipelineDataOutput] = None
    """Data for evaluating a retriever pipeline."""
