# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .sensitive_data_detection_options import SensitiveDataDetectionOptions

__all__ = ["SensitiveDataDetection"]


class SensitiveDataDetection(BaseModel):
    input: Optional[SensitiveDataDetectionOptions] = None
    """Configuration of the entities to be detected on the user input."""

    output: Optional[SensitiveDataDetectionOptions] = None
    """Configuration of the entities to be detected on the bot output."""

    recognizers: Optional[List[object]] = None
    """Additional custom recognizers.

    Check out https://microsoft.github.io/presidio/tutorial/08_no_code/ for more
    details.
    """

    retrieval: Optional[SensitiveDataDetectionOptions] = None
    """Configuration of the entities to be detected on retrieved relevant chunks."""
