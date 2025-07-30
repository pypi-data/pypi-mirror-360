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

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["NIMDeploymentConfig"]


class NIMDeploymentConfig(BaseModel):
    gpu: int
    """The number of GPUs needed for a deployment."""

    image_name: str
    """The name of the Docker image."""

    image_tag: str
    """The tag of the Docker image."""

    additional_envs: Optional[Dict[str, str]] = None
    """Additional environment variables to pass to the deployment."""

    namespace: Optional[str] = None
    """The Kubernetes namespace of the deployment."""
