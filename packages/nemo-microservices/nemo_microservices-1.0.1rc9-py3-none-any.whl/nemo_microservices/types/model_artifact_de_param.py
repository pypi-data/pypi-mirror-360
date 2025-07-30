# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .artifact_status_de import ArtifactStatusDe
from .model_precision_de import ModelPrecisionDe
from .backend_engine_type_de import BackendEngineTypeDe

__all__ = ["ModelArtifactDeParam"]


class ModelArtifactDeParam(TypedDict, total=False):
    files_url: Required[str]
    """The location where the artifact files are stored."""

    status: Required[ArtifactStatusDe]
    """The status of the model artifact."""

    backend_engine: BackendEngineTypeDe
    """Types of backend engine."""

    gpu_arch: str

    precision: ModelPrecisionDe
    """Types of model precision."""

    tensor_parallelism: int
