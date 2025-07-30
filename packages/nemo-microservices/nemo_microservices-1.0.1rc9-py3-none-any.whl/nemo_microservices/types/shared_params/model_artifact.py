# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..shared.artifact_status import ArtifactStatus
from ..shared.model_precision import ModelPrecision
from ..shared.backend_engine_type import BackendEngineType

__all__ = ["ModelArtifact"]


class ModelArtifact(TypedDict, total=False):
    files_url: Required[str]
    """The location where the artifact files are stored."""

    status: Required[ArtifactStatus]
    """Model artifact status.

    ## Values

    - `"created"` - Artifact has been created
    - `"upload_failed"` - Artifact upload has failed
    - `"upload_completed"` - Artifact upload has completed successfully
    """

    backend_engine: BackendEngineType
    """Type of backend engine.

    ## Values

    - `"nemo"` - NeMo framework engine
    - `"trt_llm"` - TensorRT-LLM engine
    - `"vllm"` - vLLM engine
    - `"faster_transformer"` - Faster Transformer engine
    - `"hugging_face"` - Hugging Face engine
    """

    gpu_arch: str
    """The GPU architecture the model is optimized for."""

    precision: ModelPrecision
    """Type of model precision.

    ## Values

    - `"int8"` - 8-bit integer precision
    - `"bf16"` - Brain floating point precision
    - `"fp16"` - 16-bit floating point precision
    - `"fp32"` - 32-bit floating point precision
    - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
      later architectures.
    - `"bf16-mixed"` - Mixed Brain floating point precision
    """

    tensor_parallelism: int
    """
    The number of GPU devices to split and process the model's neural network
    layers.
    """
