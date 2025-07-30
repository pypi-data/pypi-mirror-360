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

from ..._models import BaseModel

__all__ = ["ModelSpec"]


class ModelSpec(BaseModel):
    context_size: int
    """
    The maximum number of tokens to process together in a single forward pass
    through the model.
    """

    is_chat: bool
    """
    Indicates if the model is designed for multi-turn conversation rather than
    single-prompt completion.
    """

    num_parameters: int
    """
    The total number of trainable parameters in the model's neural network
    architecture.
    """

    num_virtual_tokens: int
    """
    The number of virtual tokens the model can support for techniques such as prompt
    tuning, where special trainable embeddings are prepended to inputs.
    """
