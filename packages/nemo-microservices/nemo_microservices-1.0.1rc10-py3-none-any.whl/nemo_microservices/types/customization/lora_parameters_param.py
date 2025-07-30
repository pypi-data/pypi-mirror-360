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

from typing import List
from typing_extensions import TypedDict

__all__ = ["LoraParametersParam"]


class LoraParametersParam(TypedDict, total=False):
    adapter_dim: int
    """Size of adapter layers added throughout the model.

    This is the size of the tunable layers that LoRA adds to various transformer
    blocks in the base model. This parameter is a power of 2.
    """

    adapter_dropout: float
    """Dropout probability in the adapter layer."""

    alpha: int
    """Scaling factor for the LoRA update.

    Controls the magnitude of the low-rank approximation. A higher alpha value
    increases the impact of the LoRA weights, effectively amplifying the changes
    made to the original model. Proper tuning of alpha is essential, as it balances
    the adaptation's impact, ensuring neither underfitting nor overfitting. This is
    often a multiple of Adapter Dimension
    """

    target_modules: List[str]
    """Target specific layers in the model architecture to apply LoRA.

    We select a subset of the layers by default. However, specific layers can also
    be selected. For example:

    - `linear_qkv`: Apply LoRA to the fused linear layer used for query, key, and
      value projections in self-attention.
    - `linear_proj`: Apply LoRA to the linear layer used for projecting the output
      of self-attention.
    - `linear_fc1`: Apply LoRA to the first fully-connected layer in MLP.
    - `linear_fc2`: Apply LoRA to the second fully-connected layer in MLP.
    - `*_proj`: Apply LoRA to all layers used for projecting the output of
      self-attention. Target modules can also contain wildcards. For example, you
      can specify
      `target_modules=['*.layers.0.*.linear_qkv', '*.layers.1.*.linear_qkv']` to add
      LoRA to only linear_qkv on the first two layers.
    """
