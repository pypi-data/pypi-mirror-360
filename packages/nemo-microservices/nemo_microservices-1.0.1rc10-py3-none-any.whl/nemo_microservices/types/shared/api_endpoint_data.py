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

from ..._compat import PYDANTIC_V2, ConfigDict
from ..._models import BaseModel
from .api_endpoint_format import APIEndpointFormat

__all__ = ["APIEndpointData"]


class APIEndpointData(BaseModel):
    model_id: str
    """The id of the model. How this is used depends on the API endpoint format."""

    url: str
    """The API endpoint URL."""

    api_key: Optional[str] = None
    """The API key that should be used to access the endpoint."""

    format: Optional[APIEndpointFormat] = None
    """API endpoint format.

    The format dictates the structure of the request and response.

    ## Values

    - `"nim"` - NVIDIA NIM format
    - `"openai"` - OpenAI format
    - `"lama_stack"` - Llama Stack format
    """

    if PYDANTIC_V2:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
