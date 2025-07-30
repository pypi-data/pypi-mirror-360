# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .generation_log import GenerationLog

__all__ = ["GuardrailsDataOutput"]


class GuardrailsDataOutput(BaseModel):
    config_ids: Optional[List[str]] = None
    """The list of configuration ids that were used."""

    llm_output: Optional[object] = None
    """Contains any additional output coming from the LLM."""

    log: Optional[GenerationLog] = None
    """Contains additional logging information associated with a generation call."""

    output_data: Optional[object] = None
    """The output data, i.e.

    a dict with the values corresponding to the `output_vars`.
    """
