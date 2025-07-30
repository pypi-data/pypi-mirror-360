# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel
from .label_selector_term import LabelSelectorTerm

__all__ = ["PreferredSchedulingTermOutput"]


class PreferredSchedulingTermOutput(BaseModel):
    preference: LabelSelectorTerm

    weight: int
