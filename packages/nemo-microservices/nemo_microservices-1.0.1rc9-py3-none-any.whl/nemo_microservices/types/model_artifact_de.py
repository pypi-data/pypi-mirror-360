# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .artifact_status_de import ArtifactStatusDe
from .model_precision_de import ModelPrecisionDe
from .backend_engine_type_de import BackendEngineTypeDe

__all__ = ["ModelArtifactDe"]


class ModelArtifactDe(BaseModel):
    files_url: str
    """The location where the artifact files are stored."""

    status: ArtifactStatusDe
    """The status of the model artifact."""

    backend_engine: Optional[BackendEngineTypeDe] = None
    """Types of backend engine."""

    gpu_arch: Optional[str] = None

    precision: Optional[ModelPrecisionDe] = None
    """Types of model precision."""

    tensor_parallelism: Optional[int] = None
