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

__all__ = ["ScoreStats"]


class ScoreStats(BaseModel):
    count: Optional[int] = None
    """The number of values used for computing the score."""

    max: Optional[float] = None
    """The maximum of all values used for computing the score."""

    mean: Optional[float] = None
    """The mean of all values used for computing the score."""

    min: Optional[float] = None
    """The minimum of all values used for computing the score."""

    stddev: Optional[float] = None
    """This is the population standard deviation, not the sample standard deviation.

            See https://towardsdatascience.com/variance-sample-vs-population-3ddbd29e498a
            for details.
    """

    stderr: Optional[float] = None
    """The standard error."""

    sum: Optional[float] = None
    """The sum of all values used for computing the score."""

    sum_squared: Optional[float] = None
    """The sum of the square of all values used for computing the score."""

    variance: Optional[float] = None
    """This is the population variance, not the sample variance.

            See https://towardsdatascience.com/variance-sample-vs-population-3ddbd29e498a
            for details.
    """
