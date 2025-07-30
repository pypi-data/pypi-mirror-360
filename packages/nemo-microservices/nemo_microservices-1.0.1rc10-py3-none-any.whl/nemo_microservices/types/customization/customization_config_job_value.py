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

from typing import Optional

from ..._models import BaseModel
from ..shared.model_precision import ModelPrecision
from ..customization_training_option import CustomizationTrainingOption

__all__ = ["CustomizationConfigJobValue"]


class CustomizationConfigJobValue(BaseModel):
    base_model: str
    """The base model that will be customized."""

    max_seq_length: int

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

    training_option: CustomizationTrainingOption
    """Resource configuration for model training.

    Specifies the hardware and parallelization settings for training.
    """

    dataset_schema: Optional[object] = None
    """Description of the expected format of the dataset"""

    prompt_template: Optional[str] = None
    """Prompt template used to extract keys from the dataset.

    E.g. prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q:
    2x2 A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'
    """
