# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .label_selector_term_param import LabelSelectorTermParam

__all__ = ["PreferredSchedulingTermInputParam"]


class PreferredSchedulingTermInputParam(TypedDict, total=False):
    preference: Required[LabelSelectorTermParam]

    weight: Required[int]
