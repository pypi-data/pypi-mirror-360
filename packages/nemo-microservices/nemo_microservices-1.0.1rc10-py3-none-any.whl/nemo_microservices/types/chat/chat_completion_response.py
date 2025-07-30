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

from typing import List, Optional

from ..._models import BaseModel
from ..shared.usage_info import UsageInfo
from ..shared.chat_completion_response_choice import ChatCompletionResponseChoice

__all__ = ["ChatCompletionResponse"]


class ChatCompletionResponse(BaseModel):
    choices: List[ChatCompletionResponseChoice]

    model: str

    usage: UsageInfo

    id: Optional[str] = None

    created: Optional[int] = None

    object: Optional[str] = None

    system_fingerprint: Optional[str] = None
    """Represents the backend configuration that the model runs with.

    Used with seed for determinism.
    """
