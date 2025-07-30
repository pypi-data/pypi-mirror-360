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

from typing import Union, Optional
from typing_extensions import TypeAlias

from .. import _models
from .base_model_filter import BaseModelFilter
from .created_at_filter import CreatedAtFilter
from .model_peft_filter import ModelPeftFilter

__all__ = ["ModelFilter", "BaseModel", "Peft"]

BaseModel: TypeAlias = Union[BaseModelFilter, str]

Peft: TypeAlias = Union[ModelPeftFilter, bool]


class ModelFilter(_models.BaseModel):
    base_model: Optional[BaseModel] = None
    """Filter models based on base model properties."""

    created_at: Optional[CreatedAtFilter] = None
    """Filter entities based on creation date."""

    namespace: Optional[str] = None
    """Filter by namespace id."""

    peft: Optional[Peft] = None
    """Filter models with Parameter Efficient Fine-tuning."""

    project: Optional[str] = None
    """Filter by project name."""

    prompt: Optional[bool] = None
    """Filter models with prompt engineering data."""
