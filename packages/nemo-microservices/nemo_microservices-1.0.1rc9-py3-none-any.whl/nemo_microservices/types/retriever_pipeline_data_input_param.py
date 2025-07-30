# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from .model_input_ev_param import ModelInputEvParam

__all__ = ["RetrieverPipelineDataInputParam", "IndexEmbeddingModel", "QueryEmbeddingModel", "RerankerModel"]

IndexEmbeddingModel: TypeAlias = Union[str, ModelInputEvParam]

QueryEmbeddingModel: TypeAlias = Union[str, ModelInputEvParam]

RerankerModel: TypeAlias = Union[str, ModelInputEvParam]


class RetrieverPipelineDataInputParam(TypedDict, total=False):
    index_embedding_model: Required[IndexEmbeddingModel]
    """The index embedding model."""

    query_embedding_model: Required[QueryEmbeddingModel]
    """The query embedding model."""

    reranker_model: RerankerModel
    """The reranker model."""

    top_k: int
    """The top k results to be used."""
