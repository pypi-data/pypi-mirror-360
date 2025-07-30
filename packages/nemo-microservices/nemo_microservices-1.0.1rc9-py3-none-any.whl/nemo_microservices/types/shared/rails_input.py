# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .input_rails import InputRails
from .action_rails import ActionRails
from .dialog_rails import DialogRails
from .output_rails import OutputRails
from .retrieval_rails import RetrievalRails
from .rails_config_data_input import RailsConfigDataInput

__all__ = ["RailsInput"]


class RailsInput(BaseModel):
    actions: Optional[ActionRails] = None
    """Configuration of action rails.

    Action rails control various options related to the execution of actions.
    Currently, only

    In the future multiple options will be added, e.g., what input validation should
    be performed per action, output validation, throttling, disabling, etc.
    """

    config: Optional[RailsConfigDataInput] = None
    """Configuration data for specific rails that are supported out-of-the-box."""

    dialog: Optional[DialogRails] = None
    """Configuration of topical rails."""

    input: Optional[InputRails] = None
    """Configuration of input rails."""

    output: Optional[OutputRails] = None
    """Configuration of output rails."""

    retrieval: Optional[RetrievalRails] = None
    """Configuration of retrieval rails."""
