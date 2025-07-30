# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List
from typing_extensions import TypedDict

__all__ = ["InjectionDetection"]


class InjectionDetection(TypedDict, total=False):
    action: str
    """Action to take.

    Options are 'reject' to offer a rejection message, 'omit' to mask the offending
    content, and 'sanitize' to pass the content as-is in the safest way. These
    options are listed in descending order of relative safety. 'sanitize' is not
    implemented at this time.
    """

    injections: List[str]
    """The list of injection types to detect.

    Options are 'sqli', 'template', 'code', 'xss'.Currently, only SQL injection,
    template injection, code injection, and markdown cross-site scripting are
    supported. Custom rules can be added, provided they are in the `yara_path` and
    have a `.yara` file extension.
    """

    yara_rules: Dict[str, str]
    """Dictionary mapping rule names to YARA rule strings.

    If provided, these rules will be used instead of loading rules from yara_path.
    Each rule should be a valid YARA rule string.
    """
