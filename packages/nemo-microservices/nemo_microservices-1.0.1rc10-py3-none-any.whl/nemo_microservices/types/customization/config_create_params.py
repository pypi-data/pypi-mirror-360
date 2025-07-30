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

from ..shared.model_precision import ModelPrecision
from ..shared_params.ownership import Ownership
from ..training_pod_spec_param import TrainingPodSpecParam
from ..customization_target_param import CustomizationTargetParam
from ..customization_training_option_param import CustomizationTrainingOptionParam

__all__ = ["ConfigCreateParams", "Target"]


class ConfigCreateParams(TypedDict, total=False):
    max_seq_length: Required[int]
    """The largest context used for training.

    Datasets are truncated based on the maximum sequence length.
    """

    training_options: Required[Iterable[CustomizationTrainingOptionParam]]
    """Resource configuration for each training option for the model."""

    chat_prompt_template: str
    """
    Chat Prompt Template to apply to the model to make it compatible with chat
    datasets
    """

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    dataset_schemas: Iterable[object]
    """Descriptions of the expected formats of the datasets uploaded."""

    description: str
    """The description of the entity."""

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

    pod_spec: TrainingPodSpecParam
    """
    Additional parameters to ensure these training jobs get run on the appropriate
    hardware.
    """

    project: str
    """The URN of the project associated with this entity."""

    prompt_template: str
    """Prompt template used to extract keys from the dataset.

    E.g. prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q:
    2x2 A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'
    """

    target: Target
    """The target to perform the customization on"""

    training_precision: ModelPrecision
    """Type of model precision.

    ## Values

    - `"int8"` - 8-bit integer precision
    - `"bf16"` - Brain floating point precision
    - `"fp16"` - 16-bit floating point precision
    - `"fp32"` - 32-bit floating point precision
    - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
      later architectures.
    - `"bf16-mixed"` - Mixed Brain floating point precision
    """


Target: TypeAlias = Union[str, CustomizationTargetParam]
