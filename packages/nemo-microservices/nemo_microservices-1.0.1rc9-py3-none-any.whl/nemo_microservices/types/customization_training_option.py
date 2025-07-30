# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .training_type import TrainingType
from .shared.finetuning_type import FinetuningType

__all__ = ["CustomizationTrainingOption"]


class CustomizationTrainingOption(BaseModel):
    finetuning_type: FinetuningType

    micro_batch_size: int
    """The number of examples per data-parallel rank.

    More details at:
    https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/nlp/nemo_megatron/batching.html
    """

    num_gpus: int
    """The number of GPUs per node to use for the specified training"""

    training_type: TrainingType

    data_parallel_size: Optional[int] = None
    """
    Number of model replicas that process different data batches in parallel, with
    gradient synchronization across GPUs. Only available on HF checkpoint models.
    data_parallel_size _ tensor_parallel_size must equal num_gpus _ num_nodes
    """

    num_nodes: Optional[int] = None
    """The number of nodes to use for the specified training"""

    pipeline_parallel_size: Optional[int] = None
    """
    Number of GPUs used to split the model across layers for pipeline model
    parallelism (inter-layer). Only available on NeMo 2 checkpoint models.
    pipeline_parallel_size _ tensor_parallel_size must equal num_gpus _ num_nodes
    """

    tensor_parallel_size: Optional[int] = None
    """
    Number of GPUs used to split individual layers for tensor model parallelism
    (intra-layer).
    """

    use_sequence_parallel: Optional[bool] = None
    """If set, sequences are distributed over multiple GPUs"""
