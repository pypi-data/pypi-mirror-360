# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from ..target_type import TargetType
from ..model_input_ev_param import ModelInputEvParam
from ..dataset_input_ev_param import DatasetInputEvParam
from ..rag_target_input_param import RagTargetInputParam
from ..shared_params.ownership import Ownership
from ..cached_outputs_data_param import CachedOutputsDataParam
from ..retriever_target_input_param import RetrieverTargetInputParam

__all__ = ["TargetCreateParams", "Dataset", "Model"]


class TargetCreateParams(TypedDict, total=False):
    type: Required[TargetType]
    """The type of the evaluation target, e.g., 'model', 'retriever', 'rag'."""

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

    name: str
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: str
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

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


Dataset: TypeAlias = Union[str, DatasetInputEvParam]

Model: TypeAlias = Union[str, ModelInputEvParam]
