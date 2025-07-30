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

from typing import List, Union
from typing_extensions import TypedDict

__all__ = ["EvaluationParamsParam"]


class EvaluationParamsParam(TypedDict, total=False):
    extra: object
    """Any other custom parameters."""

    limit_samples: int
    """Limit number of evaluation samples"""

    max_retries: int
    """Maximum number of retries for failed requests."""

    max_tokens: int
    """The maximum number of tokens to generate."""

    parallelism: int
    """Parallelism to be used for the evaluation job.

    Typically, this represents the maximum number of concurrent requests made to the
    model.
    """

    request_timeout: int
    """The timeout to be used for requests made to the model."""

    stop: Union[str, List[str]]
    """Up to 4 sequences where the API will stop generating further tokens."""

    temperature: float
    """Float value between 0 and 1.

    temp of 0 indicates greedy decoding, where the token with highest prob is
    chosen. Temperature can't be set to 0.0 currently.
    """

    top_p: float
    """
    Float value between 0 and 1; limits to the top tokens within a certain
    probability. top_p=0 means the model will only consider the single most likely
    token for the next prediction.
    """
