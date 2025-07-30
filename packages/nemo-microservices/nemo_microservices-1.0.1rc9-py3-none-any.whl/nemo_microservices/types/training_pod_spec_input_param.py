# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import TypedDict

from .toleration_param import TolerationParam
from .node_affinity_input_param import NodeAffinityInputParam

__all__ = ["TrainingPodSpecInputParam"]


class TrainingPodSpecInputParam(TypedDict, total=False):
    annotations: Dict[str, str]
    """Additional arguments for annotations"""

    node_affinity: NodeAffinityInputParam
    """The kubernentes node affinity to apply to the training pods"""

    node_selectors: Dict[str, str]
    """Additional arguments for node selector"""

    tolerations: Iterable[TolerationParam]
    """Additional arguments for tolerations"""
