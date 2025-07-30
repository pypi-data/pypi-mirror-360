# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .cached_outputs_data_param import CachedOutputsDataParam
from .retriever_pipeline_data_input_param import RetrieverPipelineDataInputParam

__all__ = ["RetrieverTargetInputParam"]


class RetrieverTargetInputParam(TypedDict, total=False):
    cached_outputs: CachedOutputsDataParam
    """An evaluation target which contains cached outputs."""

    pipeline: RetrieverPipelineDataInputParam
    """Data for evaluating a retriever pipeline."""
