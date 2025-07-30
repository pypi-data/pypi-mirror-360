# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .address_v1_param import AddressV1Param
from .industry_v1_param import IndustryV1Param
from .support_channels_v1_param import SupportChannelsV1Param

__all__ = ["BusinessProfileV1Param"]


class BusinessProfileV1Param(TypedDict, total=False):
    name: Required[str]
    """The operating or trade name of the business."""

    website: Required[str]
    """URL of the business's primary marketing website."""

    address: Optional[AddressV1Param]
    """The address object is optional. If provided, it must be a valid address."""

    description: Optional[str]
    """A brief description of the business and its products or services."""

    industry: IndustryV1Param

    legal_name: Optional[str]
    """The official registered name of the business."""

    phone: Optional[str]
    """The primary contact phone number for the business."""

    support_channels: SupportChannelsV1Param

    tax_id: Optional[str]
    """The business's tax identification number (e.g., EIN in the US)."""

    use_case: Optional[str]
    """A description of how the business intends to use Straddle's services."""
