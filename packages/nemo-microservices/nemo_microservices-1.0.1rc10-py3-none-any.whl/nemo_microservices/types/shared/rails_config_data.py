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
from .fiddler_guardrails import FiddlerGuardrails
from .clavata_rail_config import ClavataRailConfig
from .injection_detection import InjectionDetection
from .patronus_rail_config import PatronusRailConfig
from .private_ai_detection import PrivateAIDetection
from .auto_align_rail_config import AutoAlignRailConfig
from .sensitive_data_detection import SensitiveDataDetection
from .fact_checking_rail_config import FactCheckingRailConfig
from .jailbreak_detection_config import JailbreakDetectionConfig

__all__ = ["RailsConfigData"]


class RailsConfigData(BaseModel):
    autoalign: Optional[AutoAlignRailConfig] = None
    """Configuration data for the AutoAlign API"""

    clavata: Optional[ClavataRailConfig] = None
    """Configuration data for the Clavata API"""

    fact_checking: Optional[FactCheckingRailConfig] = None
    """Configuration data for the fact-checking rail."""

    fiddler: Optional[FiddlerGuardrails] = None
    """Configuration for Fiddler Guardrails."""

    injection_detection: Optional[InjectionDetection] = None
    """Configuration for injection detection."""

    jailbreak_detection: Optional[JailbreakDetectionConfig] = None
    """Configuration data for jailbreak detection."""

    patronus: Optional[PatronusRailConfig] = None
    """Configuration data for the Patronus Evaluate API"""

    privateai: Optional[PrivateAIDetection] = None
    """Configuration for Private AI."""

    sensitive_data_detection: Optional[SensitiveDataDetection] = None
    """Configuration of what sensitive data should be detected."""
