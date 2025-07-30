# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TermsOfServiceV1Param"]


class TermsOfServiceV1Param(TypedDict, total=False):
    accepted_date: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]
    """The datetime of when the terms of service were accepted, in ISO 8601 format."""

    agreement_type: Required[Literal["embedded", "direct"]]
    """The type or version of the agreement accepted.

    Use `embedded` unless your platform was specifically enabled for `direct`
    agreements.
    """

    agreement_url: Required[Optional[str]]
    """The URL where the full text of the accepted agreement can be found."""

    accepted_ip: Optional[str]
    """The IP address from which the terms of service were accepted."""

    accepted_user_agent: Optional[str]
    """The user agent string of the browser or application used to accept the terms."""
