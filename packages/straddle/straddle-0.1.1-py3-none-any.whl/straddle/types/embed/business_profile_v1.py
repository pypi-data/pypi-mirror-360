# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .address_v1 import AddressV1
from .industry_v1 import IndustryV1
from .support_channels_v1 import SupportChannelsV1

__all__ = ["BusinessProfileV1"]


class BusinessProfileV1(BaseModel):
    name: str
    """The operating or trade name of the business."""

    website: str
    """URL of the business's primary marketing website."""

    address: Optional[AddressV1] = None
    """The address object is optional. If provided, it must be a valid address."""

    description: Optional[str] = None
    """A brief description of the business and its products or services."""

    industry: Optional[IndustryV1] = None

    legal_name: Optional[str] = None
    """The official registered name of the business."""

    phone: Optional[str] = None
    """The primary contact phone number for the business."""

    support_channels: Optional[SupportChannelsV1] = None

    tax_id: Optional[str] = None
    """The business's tax identification number (e.g., EIN in the US)."""

    use_case: Optional[str] = None
    """A description of how the business intends to use Straddle's services."""
