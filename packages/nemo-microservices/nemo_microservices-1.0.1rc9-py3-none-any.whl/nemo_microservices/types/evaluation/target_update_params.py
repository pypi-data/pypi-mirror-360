# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from ..target_type import TargetType
from ..dataset_ev_param import DatasetEvParam
from ..model_input_ev_param import ModelInputEvParam
from ..rag_target_input_param import RagTargetInputParam
from ..shared_params.ownership import Ownership
from ..cached_outputs_data_param import CachedOutputsDataParam
from ..retriever_target_input_param import RetrieverTargetInputParam

__all__ = ["TargetUpdateParams", "Dataset", "Model"]


class TargetUpdateParams(TypedDict, total=False):
    namespace: Required[str]

    cached_outputs: CachedOutputsDataParam
    """An evaluation target which contains cached outputs."""

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    dataset: Dataset
    """Dataset to be evaluated."""

    description: str
    """The description of the entity."""

    model: Model
    """The model to be evaluated."""

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The URN of the project associated with this entity."""

    rag: RagTargetInputParam
    """RAG to be evaluated."""

    retriever: RetrieverTargetInputParam
    """Retriever to be evaluated."""

    rows: Iterable[object]
    """Rows to be evaluated."""

    type: TargetType
    """The type of the evaluation target, e.g., 'model', 'retriever', 'rag'."""


Dataset: TypeAlias = Union[str, DatasetEvParam]

Model: TypeAlias = Union[str, ModelInputEvParam]
