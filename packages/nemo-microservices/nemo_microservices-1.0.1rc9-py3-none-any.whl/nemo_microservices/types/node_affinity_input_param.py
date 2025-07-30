# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .node_selector_input_param import NodeSelectorInputParam
from .preferred_scheduling_term_input_param import PreferredSchedulingTermInputParam

__all__ = ["NodeAffinityInputParam"]


class NodeAffinityInputParam(TypedDict, total=False):
    preferred_during_scheduling_ignored_during_execution: Annotated[
        Iterable[PreferredSchedulingTermInputParam],
        PropertyInfo(alias="preferredDuringSchedulingIgnoredDuringExecution"),
    ]

    required_during_scheduling_ignored_during_execution: Annotated[
        NodeSelectorInputParam, PropertyInfo(alias="requiredDuringSchedulingIgnoredDuringExecution")
    ]
