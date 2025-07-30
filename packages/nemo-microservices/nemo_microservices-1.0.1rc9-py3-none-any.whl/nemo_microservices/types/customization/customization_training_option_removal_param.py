# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..training_type import TrainingType
from ..shared.finetuning_type import FinetuningType

__all__ = ["CustomizationTrainingOptionRemovalParam"]


class CustomizationTrainingOptionRemovalParam(TypedDict, total=False):
    finetuning_type: Required[FinetuningType]

    training_type: Required[TrainingType]
