# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel
from .model_output_ev import ModelOutputEv

__all__ = ["RetrieverPipelineDataOutput", "IndexEmbeddingModel", "QueryEmbeddingModel", "RerankerModel"]

IndexEmbeddingModel: TypeAlias = Union[str, ModelOutputEv]

QueryEmbeddingModel: TypeAlias = Union[str, ModelOutputEv]

RerankerModel: TypeAlias = Union[str, ModelOutputEv]


class RetrieverPipelineDataOutput(BaseModel):
    index_embedding_model: IndexEmbeddingModel
    """The index embedding model."""

    query_embedding_model: QueryEmbeddingModel
    """The query embedding model."""

    reranker_model: Optional[RerankerModel] = None
    """The reranker model."""

    top_k: Optional[int] = None
    """The top k results to be used."""
