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

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from .._models import BaseModel
from .shared.ownership import Ownership
from .training_pod_spec import TrainingPodSpec
from .customization_target import CustomizationTarget
from .shared.model_precision import ModelPrecision
from .customization_training_option import CustomizationTrainingOption

__all__ = ["CustomizationConfig", "Target"]

Target: TypeAlias = Union[str, CustomizationTarget]


class CustomizationConfig(BaseModel):
    max_seq_length: int
    """The largest context used for training.

    Datasets are truncated based on the maximum sequence length.
    """

    training_options: List[CustomizationTrainingOption]
    """Resource configuration for each training option for the model."""

    chat_prompt_template: Optional[str] = None
    """
    Chat Prompt Template to apply to the model to make it compatible with chat
    datasets
    """

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    dataset_schemas: Optional[List[object]] = None
    """Descriptions of the expected formats of the datasets uploaded."""

    description: Optional[str] = None
    """The description of the entity."""

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

    pod_spec: Optional[TrainingPodSpec] = None
    """
    Additional parameters to ensure these training jobs get run on the appropriate
    hardware.
    """

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    prompt_template: Optional[str] = None
    """Prompt template used to extract keys from the dataset.

    E.g. prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q:
    2x2 A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'
    """

    target: Optional[Target] = None
    """The target to perform the customization on"""

    training_precision: Optional[ModelPrecision] = None
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

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""
