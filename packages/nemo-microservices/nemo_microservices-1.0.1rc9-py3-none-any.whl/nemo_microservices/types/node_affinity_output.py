# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .node_selector_output import NodeSelectorOutput
from .preferred_scheduling_term_output import PreferredSchedulingTermOutput

__all__ = ["NodeAffinityOutput"]


class NodeAffinityOutput(BaseModel):
    preferred_during_scheduling_ignored_during_execution: Optional[List[PreferredSchedulingTermOutput]] = FieldInfo(
        alias="preferredDuringSchedulingIgnoredDuringExecution", default=None
    )

    required_during_scheduling_ignored_during_execution: Optional[NodeSelectorOutput] = FieldInfo(
        alias="requiredDuringSchedulingIgnoredDuringExecution", default=None
    )
