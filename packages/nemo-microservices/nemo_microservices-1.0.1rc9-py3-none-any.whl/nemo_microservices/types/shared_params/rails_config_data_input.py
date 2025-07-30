# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .fiddler_guardrails import FiddlerGuardrails
from .clavata_rail_config import ClavataRailConfig
from .injection_detection import InjectionDetection
from .private_ai_detection import PrivateAIDetection
from .auto_align_rail_config import AutoAlignRailConfig
from .sensitive_data_detection import SensitiveDataDetection
from .fact_checking_rail_config import FactCheckingRailConfig
from .jailbreak_detection_config import JailbreakDetectionConfig
from .patronus_rail_config_input import PatronusRailConfigInput

__all__ = ["RailsConfigDataInput"]


class RailsConfigDataInput(TypedDict, total=False):
    autoalign: AutoAlignRailConfig
    """Configuration data for the AutoAlign API"""

    clavata: ClavataRailConfig
    """Configuration data for the Clavata API"""

    fact_checking: FactCheckingRailConfig
    """Configuration data for the fact-checking rail."""

    fiddler: FiddlerGuardrails
    """Configuration for Fiddler Guardrails."""

    injection_detection: InjectionDetection
    """Configuration for injection detection."""

    jailbreak_detection: JailbreakDetectionConfig
    """Configuration data for jailbreak detection."""

    patronus: PatronusRailConfigInput
    """Configuration data for the Patronus Evaluate API"""

    privateai: PrivateAIDetection
    """Configuration for Private AI."""

    sensitive_data_detection: SensitiveDataDetection
    """Configuration of what sensitive data should be detected."""
