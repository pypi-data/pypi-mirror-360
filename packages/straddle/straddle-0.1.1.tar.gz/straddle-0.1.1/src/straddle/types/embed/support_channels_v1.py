# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["SupportChannelsV1"]


class SupportChannelsV1(BaseModel):
    email: Optional[str] = None
    """The email address for customer support inquiries."""

    phone: Optional[str] = None
    """The phone number for customer support."""

    url: Optional[str] = None
    """The URL of the business's customer support page or contact form."""
