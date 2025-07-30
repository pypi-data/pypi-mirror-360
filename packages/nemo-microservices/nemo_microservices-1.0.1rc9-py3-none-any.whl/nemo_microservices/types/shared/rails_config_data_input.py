# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
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


class RailsConfigDataInput(BaseModel):
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

    patronus: Optional[PatronusRailConfigInput] = None
    """Configuration data for the Patronus Evaluate API"""

    privateai: Optional[PrivateAIDetection] = None
    """Configuration for Private AI."""

    sensitive_data_detection: Optional[SensitiveDataDetection] = None
    """Configuration of what sensitive data should be detected."""
