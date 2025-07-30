# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Required, TypeAlias, TypedDict

from .message_template import MessageTemplate

__all__ = ["TaskPrompt", "Message"]

Message: TypeAlias = Union[MessageTemplate, str]


class TaskPrompt(TypedDict, total=False):
    task: Required[str]
    """The id of the task associated with this prompt."""

    content: str
    """The content of the prompt, if it's a string."""

    max_length: int
    """The maximum length of the prompt in number of characters."""

    max_tokens: int
    """The maximum number of tokens that can be generated in the chat completion."""

    messages: List[Message]
    """The list of messages included in the prompt. Used for chat models."""

    mode: str
    """Corresponds to the `prompting_mode` for which this prompt is fetched.

    Default is 'standard'.
    """

    models: List[str]
    """If specified, the prompt will be used only for the given LLM engines/models.

    The format is a list of strings with the format: <engine> or <engine>/<model>.
    """

    output_parser: str
    """The name of the output parser to use for this prompt."""

    stop: List[str]
    """If specified, will be configure stop tokens for models that support this."""
