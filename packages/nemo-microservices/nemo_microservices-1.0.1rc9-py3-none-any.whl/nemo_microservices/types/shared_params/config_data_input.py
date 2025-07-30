# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .model import Model
from .instruction import Instruction
from .rails_input import RailsInput
from .task_prompt import TaskPrompt

__all__ = ["ConfigDataInput"]


class ConfigDataInput(TypedDict, total=False):
    models: Required[Iterable[Model]]
    """The list of models used by the rails configuration."""

    actions_server_url: str
    """The URL of the actions server that should be used for the rails."""

    colang_version: str
    """The Colang version to use."""

    custom_data: object
    """Any custom configuration data that might be needed."""

    enable_multi_step_generation: bool
    """Whether to enable multi-step generation for the LLM."""

    enable_rails_exceptions: bool
    """
    If set, the pre-defined guardrails raise exceptions instead of returning
    pre-defined messages.
    """

    instructions: Iterable[Instruction]
    """List of instructions in natural language that the LLM should use."""

    lowest_temperature: float
    """The lowest temperature that should be used for the LLM."""

    passthrough: bool
    """
    Weather the original prompt should pass through the guardrails configuration as
    is. This means it will not be altered in any way.
    """

    prompting_mode: str
    """Allows choosing between different prompting strategies."""

    prompts: Iterable[TaskPrompt]
    """The prompts that should be used for the various LLM tasks."""

    rails: RailsInput
    """Configuration of specific rails."""

    sample_conversation: str
    """The sample conversation that should be used inside the prompts."""
