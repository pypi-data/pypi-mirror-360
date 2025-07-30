# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .label_selector_requirement_param import LabelSelectorRequirementParam

__all__ = ["LabelSelectorTermParam"]


class LabelSelectorTermParam(TypedDict, total=False):
    match_expressions: Annotated[Iterable[LabelSelectorRequirementParam], PropertyInfo(alias="matchExpressions")]
