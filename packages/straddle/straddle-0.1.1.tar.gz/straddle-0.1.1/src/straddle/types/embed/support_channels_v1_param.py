# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["SupportChannelsV1Param"]


class SupportChannelsV1Param(TypedDict, total=False):
    email: Optional[str]
    """The email address for customer support inquiries."""

    phone: Optional[str]
    """The phone number for customer support."""

    url: Optional[str]
    """The URL of the business's customer support page or contact form."""
