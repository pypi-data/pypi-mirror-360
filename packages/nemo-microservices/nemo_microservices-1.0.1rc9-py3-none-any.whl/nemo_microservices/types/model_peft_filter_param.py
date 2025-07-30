# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ModelPeftFilterParam"]


class ModelPeftFilterParam(TypedDict, total=False):
    lora: bool
    """Filter models with LoRA fine-tuning."""
