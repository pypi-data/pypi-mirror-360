# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .message_template import MessageTemplate

__all__ = ["TaskPrompt", "Message"]

Message: TypeAlias = Union[MessageTemplate, str]


class TaskPrompt(BaseModel):
    task: str
    """The id of the task associated with this prompt."""

    content: Optional[str] = None
    """The content of the prompt, if it's a string."""

    max_length: Optional[int] = None
    """The maximum length of the prompt in number of characters."""

    max_tokens: Optional[int] = None
    """The maximum number of tokens that can be generated in the chat completion."""

    messages: Optional[List[Message]] = None
    """The list of messages included in the prompt. Used for chat models."""

    mode: Optional[str] = None
    """Corresponds to the `prompting_mode` for which this prompt is fetched.

    Default is 'standard'.
    """

    models: Optional[List[str]] = None
    """If specified, the prompt will be used only for the given LLM engines/models.

    The format is a list of strings with the format: <engine> or <engine>/<model>.
    """

    output_parser: Optional[str] = None
    """The name of the output parser to use for this prompt."""

    stop: Optional[List[str]] = None
    """If specified, will be configure stop tokens for models that support this."""
