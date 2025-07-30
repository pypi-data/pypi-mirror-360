# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypeAlias

__all__ = ["BackendEngineType"]

BackendEngineType: TypeAlias = Literal["nemo", "trt_llm", "vllm", "faster_transformer", "hugging_face"]
