# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .input_rails import InputRails
from .action_rails import ActionRails
from .dialog_rails import DialogRails
from .output_rails import OutputRails
from .retrieval_rails import RetrievalRails
from .rails_config_data_input import RailsConfigDataInput

__all__ = ["RailsInput"]


class RailsInput(TypedDict, total=False):
    actions: ActionRails
    """Configuration of action rails.

    Action rails control various options related to the execution of actions.
    Currently, only

    In the future multiple options will be added, e.g., what input validation should
    be performed per action, output validation, throttling, disabling, etc.
    """

    config: RailsConfigDataInput
    """Configuration data for specific rails that are supported out-of-the-box."""

    dialog: DialogRails
    """Configuration of topical rails."""

    input: InputRails
    """Configuration of input rails."""

    output: OutputRails
    """Configuration of output rails."""

    retrieval: RetrievalRails
    """Configuration of retrieval rails."""
