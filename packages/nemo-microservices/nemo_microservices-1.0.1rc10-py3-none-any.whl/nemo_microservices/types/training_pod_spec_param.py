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

from typing import Dict, Iterable
from typing_extensions import TypedDict

from .toleration_param import TolerationParam
from .node_affinity_param import NodeAffinityParam

__all__ = ["TrainingPodSpecParam"]


class TrainingPodSpecParam(TypedDict, total=False):
    annotations: Dict[str, str]
    """Additional arguments for annotations"""

    node_affinity: NodeAffinityParam
    """The kubernentes node affinity to apply to the training pods"""

    node_selectors: Dict[str, str]
    """Additional arguments for node selector"""

    tolerations: Iterable[TolerationParam]
    """Additional arguments for tolerations"""
