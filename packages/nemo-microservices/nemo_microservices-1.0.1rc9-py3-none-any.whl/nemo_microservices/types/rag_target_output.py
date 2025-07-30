# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .cached_outputs_data import CachedOutputsData
from .rag_pipeline_data_output import RagPipelineDataOutput

__all__ = ["RagTargetOutput"]


class RagTargetOutput(BaseModel):
    cached_outputs: Optional[CachedOutputsData] = None
    """An evaluation target which contains cached outputs."""

    pipeline: Optional[RagPipelineDataOutput] = None
    """Data for evaluating a RAG pipeline."""
