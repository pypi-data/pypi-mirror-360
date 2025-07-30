# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .node_selector_term import NodeSelectorTerm

__all__ = ["NodeSelectorOutput"]


class NodeSelectorOutput(BaseModel):
    node_selector_terms: List[NodeSelectorTerm] = FieldInfo(alias="nodeSelectorTerms")
