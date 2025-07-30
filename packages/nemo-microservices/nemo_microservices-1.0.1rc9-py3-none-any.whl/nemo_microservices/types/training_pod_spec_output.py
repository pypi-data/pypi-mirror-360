# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel
from .toleration import Toleration
from .node_affinity_output import NodeAffinityOutput

__all__ = ["TrainingPodSpecOutput"]


class TrainingPodSpecOutput(BaseModel):
    annotations: Optional[Dict[str, str]] = None
    """Additional arguments for annotations"""

    node_affinity: Optional[NodeAffinityOutput] = None
    """The kubernentes node affinity to apply to the training pods"""

    node_selectors: Optional[Dict[str, str]] = None
    """Additional arguments for node selector"""

    tolerations: Optional[List[Toleration]] = None
    """Additional arguments for tolerations"""
