# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["CustomizationConfigFilterParam"]


class CustomizationConfigFilterParam(TypedDict, total=False):
    enabled: bool
    """Filter by whether the target is enabled or not for customization"""

    finetuning_type: str
    """Filter by the finetuning type"""

    name: str
    """Filter by the name of the customization config"""

    target_base_model: str
    """Filter by name of the target's base model."""

    target_name: str
    """Filter by name of the target."""

    training_type: str
    """Filter by the training type"""
