# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import date
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["RepresentativeCreateParams", "Relationship"]


class RepresentativeCreateParams(TypedDict, total=False):
    account_id: Required[str]
    """The unique identifier of the account this representative is associated with."""

    dob: Required[Annotated[Union[str, date], PropertyInfo(format="iso8601")]]
    """Date of birth for the representative in ISO 8601 format (YYYY-MM-DD)."""

    email: Required[str]
    """The company email address of the representative."""

    first_name: Required[str]
    """The first name of the representative."""

    last_name: Required[str]
    """The last name of the representative."""

    mobile_number: Required[str]
    """The mobile phone number of the representative."""

    relationship: Required[Relationship]

    ssn_last4: Required[str]
    """The last 4 digits of the representative's Social Security Number."""

    external_id: Optional[str]
    """
    Unique identifier for the representative in your database, used for
    cross-referencing between Straddle and your systems.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]


class Relationship(TypedDict, total=False):
    control: Required[bool]
    """
    Whether the representative has significant responsibility to control, manage, or
    direct the organization. One representative must be identified under the control
    prong for each legal entity.
    """

    owner: Required[bool]
    """
    Whether the representative owns any percentage of of the equity interests of the
    legal entity.
    """

    primary: Required[bool]
    """Whether the person is authorized as the primary representative of the account.

    This is the person chosen by the business to provide information about
    themselves, general information about the account, and who consented to the
    services agreement.

    There can be only one primary representative for an account at a time.
    """

    percent_ownership: Optional[float]
    """The percentage of ownership the representative has.

    Required if 'Owner' is true.
    """

    title: Optional[str]
    """The job title of the representative."""
