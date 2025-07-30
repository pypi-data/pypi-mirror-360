# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .tool_schema_output import ToolSchemaOutput

__all__ = ["DatasetParametersOutput"]


class DatasetParametersOutput(BaseModel):
    tools: Optional[List[ToolSchemaOutput]] = None
    """A list of tools that are available for training with tool calling"""
