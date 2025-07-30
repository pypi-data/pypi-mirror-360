# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["IndustryV1Param"]


class IndustryV1Param(TypedDict, total=False):
    category: Optional[str]
    """The general category of the industry. Required if not providing MCC."""

    mcc: Optional[str]
    """The Merchant Category Code (MCC) that best describes the business. Optional."""

    sector: Optional[str]
    """The specific sector within the industry category.

    Required if not providing MCC.
    """
