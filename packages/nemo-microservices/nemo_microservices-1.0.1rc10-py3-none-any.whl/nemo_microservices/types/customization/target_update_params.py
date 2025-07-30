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

from typing_extensions import Required, TypedDict

from ..shared.model_precision import ModelPrecision

__all__ = ["TargetUpdateParams"]


class TargetUpdateParams(TypedDict, total=False):
    namespace: Required[str]

    base_model: str
    """
    Default to being the same as the the configuration entry name, maps to the name
    in NIM
    """

    description: str
    """The description of the entity."""

    enabled: bool
    """Enable the model for training jobs"""

    hf_endpoint: str
    """Configure the Hub base URL.

    Defaults to NeMo Data Store. Set value as "https://huggingface.co" to download
    model_uri from HuggingFace.
    """

    model_path: str
    """Path to the model checkpoints to use for training.

    Absolute path or local path from the models cache
    """

    model_uri: str
    """The URI of the model to download to the model cache at the model_path directory.

    To download from NGC, specify ngc://org/optional-team/model-name:version. To
    download from Nemo Data Store, specify hf://namespace/model-name@checkpoint-name
    """

    num_parameters: int
    """Number of parameters used for training the model"""

    precision: ModelPrecision
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

    project: str
    """The URN of the project associated with this entity."""

    tokenizer: object
    """Overrides for the model tokenizer"""
