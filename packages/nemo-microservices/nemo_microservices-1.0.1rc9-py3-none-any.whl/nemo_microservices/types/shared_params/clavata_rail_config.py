# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, TypedDict

from .clavata_rail_options import ClavataRailOptions

__all__ = ["ClavataRailConfig"]


class ClavataRailConfig(TypedDict, total=False):
    input: ClavataRailOptions
    """Configuration data for the Clavata API"""

    label_match_logic: Literal["ANY", "ALL"]
    """
    The logic to use when deciding whether the evaluation matched. If ANY, only one
    of the configured labels needs to be found in the input or output. If ALL, all
    configured labels must be found in the input or output.
    """

    output: ClavataRailOptions
    """Configuration data for the Clavata API"""

    policies: Dict[str, str]
    """A dictionary of policy aliases and their corresponding IDs."""

    server_endpoint: str
    """The endpoint for the Clavata API"""
