# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import TypedDict

__all__ = ["GenerationRailsOptionsParam"]


class GenerationRailsOptionsParam(TypedDict, total=False):
    dialog: bool
    """Whether the dialog rails are enabled or not."""

    input: Union[bool, List[str]]
    """Whether the input rails are enabled or not.

    If a list of names is specified, then only the specified input rails will be
    applied.
    """

    output: Union[bool, List[str]]
    """Whether the output rails are enabled or not.

    If a list of names is specified, then only the specified output rails will be
    applied.
    """

    retrieval: Union[bool, List[str]]
    """Whether the retrieval rails are enabled or not.

    If a list of names is specified, then only the specified retrieval rails will be
    applied.
    """
