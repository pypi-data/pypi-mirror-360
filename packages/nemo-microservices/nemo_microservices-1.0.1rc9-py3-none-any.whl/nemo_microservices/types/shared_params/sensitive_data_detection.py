# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

from .sensitive_data_detection_options import SensitiveDataDetectionOptions

__all__ = ["SensitiveDataDetection"]


class SensitiveDataDetection(TypedDict, total=False):
    input: SensitiveDataDetectionOptions
    """Configuration of the entities to be detected on the user input."""

    output: SensitiveDataDetectionOptions
    """Configuration of the entities to be detected on the bot output."""

    recognizers: Iterable[object]
    """Additional custom recognizers.

    Check out https://microsoft.github.io/presidio/tutorial/08_no_code/ for more
    details.
    """

    retrieval: SensitiveDataDetectionOptions
    """Configuration of the entities to be detected on retrieved relevant chunks."""
