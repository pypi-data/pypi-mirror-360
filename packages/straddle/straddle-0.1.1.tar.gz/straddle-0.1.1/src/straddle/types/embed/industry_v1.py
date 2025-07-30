# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["IndustryV1"]


class IndustryV1(BaseModel):
    category: Optional[str] = None
    """The general category of the industry. Required if not providing MCC."""

    mcc: Optional[str] = None
    """The Merchant Category Code (MCC) that best describes the business. Optional."""

    sector: Optional[str] = None
    """The specific sector within the industry category.

    Required if not providing MCC.
    """
