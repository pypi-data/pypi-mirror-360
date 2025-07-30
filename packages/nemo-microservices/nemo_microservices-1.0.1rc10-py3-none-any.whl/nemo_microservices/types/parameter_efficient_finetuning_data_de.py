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

from .._models import BaseModel
from .finetuning_type_de import FinetuningTypeDe
from .shared.lora_finetuning_data import LoraFinetuningData
from .shared.p_tuning_finetuning_data import PTuningFinetuningData

__all__ = ["ParameterEfficientFinetuningDataDe"]


class ParameterEfficientFinetuningDataDe(BaseModel):
    finetuning_type: FinetuningTypeDe
    """The type of finetuning."""

    lora: Optional[LoraFinetuningData] = None
    """Data about a LoRA fine-tuned model."""

    p_tuning: Optional[PTuningFinetuningData] = None
    """Data about a p-tuned model."""
