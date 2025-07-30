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

__all__ = ["ReasoningParams"]


class ReasoningParams(BaseModel):
    effort: Optional[str] = None
    """
    Option for OpenAI models to specify low, medium, or high reasoning effort which
    balances between speed and reasoning accuracy.
    """

    end_token: Optional[str] = None
    """
    Configure the end token to trim reasoning context based on the model's reasoning
    API. Used for omitting Nemotron reasoning steps from output denoted with
    </think> tags
    """
