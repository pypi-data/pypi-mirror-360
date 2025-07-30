# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from ..._models import BaseModel
from ..dataset_ev import DatasetEv
from ..target_type import TargetType
from ..model_output_ev import ModelOutputEv
from ..shared.ownership import Ownership
from ..rag_target_output import RagTargetOutput
from ..cached_outputs_data import CachedOutputsData
from ..retriever_target_output import RetrieverTargetOutput

__all__ = ["EvaluationTarget", "Dataset", "Model"]

Dataset: TypeAlias = Union[str, DatasetEv]

Model: TypeAlias = Union[str, ModelOutputEv]


class EvaluationTarget(BaseModel):
    type: TargetType
    """The type of the evaluation target, e.g., 'model', 'retriever', 'rag'."""

    id: Optional[str] = None
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    cached_outputs: Optional[CachedOutputsData] = None
    """An evaluation target which contains cached outputs."""

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[Dict[str, str]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    dataset: Optional[Dataset] = None
    """Dataset to be evaluated."""

    description: Optional[str] = None
    """The description of the entity."""

    model: Optional[Model] = None
    """The model to be evaluated."""

    name: Optional[str] = None
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: Optional[str] = None
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    rag: Optional[RagTargetOutput] = None
    """RAG to be evaluated."""

    retriever: Optional[RetrieverTargetOutput] = None
    """Retriever to be evaluated."""

    rows: Optional[List[object]] = None
    """Rows to be evaluated."""

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""
