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

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from ..target_type import TargetType
from ..model_ev_param import ModelEvParam
from ..dataset_ev_param import DatasetEvParam
from ..rag_target_param import RagTargetParam
from ..retriever_target_param import RetrieverTargetParam
from ..shared_params.ownership import Ownership
from ..cached_outputs_data_param import CachedOutputsDataParam

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

    rag: RagTargetParam
    """RAG to be evaluated."""

    retriever: RetrieverTargetParam
    """Retriever to be evaluated."""

    rows: Iterable[object]
    """Rows to be evaluated."""

    type: TargetType
    """The type of the evaluation target, e.g., 'model', 'retriever', 'rag'."""


Dataset: TypeAlias = Union[str, DatasetEvParam]

Model: TypeAlias = Union[str, ModelEvParam]
