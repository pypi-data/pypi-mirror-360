# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .node_selector_term_param import NodeSelectorTermParam

__all__ = ["NodeSelectorInputParam"]


class NodeSelectorInputParam(TypedDict, total=False):
    node_selector_terms: Required[Annotated[Iterable[NodeSelectorTermParam], PropertyInfo(alias="nodeSelectorTerms")]]
