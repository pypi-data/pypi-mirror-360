# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel
from .model_output_ev import ModelOutputEv
from .retriever_target_output import RetrieverTargetOutput

__all__ = ["RagPipelineDataOutput", "Model"]

Model: TypeAlias = Union[str, ModelOutputEv]


class RagPipelineDataOutput(BaseModel):
    model: Model
    """The generation model for the RAG pipeline."""

    retriever: RetrieverTargetOutput
    """The retriever pipeline included in the RAG pipeline."""

    context_ordering: Optional[str] = None
    """The context ordering for the RAG pipeline."""
