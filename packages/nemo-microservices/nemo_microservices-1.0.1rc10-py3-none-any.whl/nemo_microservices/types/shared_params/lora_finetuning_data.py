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

__all__ = ["LoraFinetuningData"]


class LoraFinetuningData(TypedDict, total=False):
    alpha: Required[int]
    """
    A scaling factor that controls how much influence the LoRA adaptations have on
    the base model's behavior. The alpha parameter should typically be set to dim or
    0.5 \\** dim as the actual scaling applied in the training loop is alpha / dim.
    """

    apply_lora_to_mlp: Required[bool]
    """
    Controls whether to adapt the model's feed-forward neural network layers using
    LoRA.
    """

    apply_lora_to_output: Required[bool]
    """Controls whether to adapt the model's final output layer using LoRA."""
