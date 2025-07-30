# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .label_selector_requirement import LabelSelectorRequirement

__all__ = ["NodeSelectorTerm"]


class NodeSelectorTerm(BaseModel):
    match_expressions: Optional[List[LabelSelectorRequirement]] = FieldInfo(alias="matchExpressions", default=None)
