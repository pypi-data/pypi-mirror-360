# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["TermsOfServiceV1"]


class TermsOfServiceV1(BaseModel):
    accepted_date: datetime
    """The datetime of when the terms of service were accepted, in ISO 8601 format."""

    agreement_type: Literal["embedded", "direct"]
    """The type or version of the agreement accepted.

    Use `embedded` unless your platform was specifically enabled for `direct`
    agreements.
    """

    agreement_url: Optional[str] = None
    """The URL where the full text of the accepted agreement can be found."""

    accepted_ip: Optional[str] = None
    """The IP address from which the terms of service were accepted."""

    accepted_user_agent: Optional[str] = None
    """The user agent string of the browser or application used to accept the terms."""
