# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from .._models import BaseModel
from .model_ev import ModelEv
from .dataset_ev import DatasetEv
from .rag_target import RagTarget
from .target_type import TargetType
from .retriever_target import RetrieverTarget
from .shared.ownership import Ownership
from .cached_outputs_data import CachedOutputsData

__all__ = ["EvaluationTarget", "Dataset", "Model"]

Dataset: TypeAlias = Union[str, DatasetEv]

Model: TypeAlias = Union[str, ModelEv]


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

    rag: Optional[RagTarget] = None
    """RAG to be evaluated."""

    retriever: Optional[RetrieverTarget] = None
    """Retriever to be evaluated."""

    rows: Optional[List[object]] = None
    """Rows to be evaluated."""

    schema_version: Optional[str] = None
    """The version of the schema for the object. Internal use only."""

    type_prefix: Optional[str] = None

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""
