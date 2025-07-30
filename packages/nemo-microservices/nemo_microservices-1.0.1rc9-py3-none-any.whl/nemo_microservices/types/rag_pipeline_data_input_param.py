# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from .model_input_ev_param import ModelInputEvParam
from .retriever_target_input_param import RetrieverTargetInputParam

__all__ = ["RagPipelineDataInputParam", "Model"]

Model: TypeAlias = Union[str, ModelInputEvParam]


class RagPipelineDataInputParam(TypedDict, total=False):
    model: Required[Model]
    """The generation model for the RAG pipeline."""

    retriever: Required[RetrieverTargetInputParam]
    """The retriever pipeline included in the RAG pipeline."""

    context_ordering: str
    """The context ordering for the RAG pipeline."""
