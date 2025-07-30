# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DistillationParametersParam"]


class DistillationParametersParam(TypedDict, total=False):
    teacher: Required[str]
    """Target to be used as teacher for distillation."""
