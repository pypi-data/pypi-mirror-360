# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "CapabilityRequestCreateParams",
    "Businesses",
    "Charges",
    "Individuals",
    "Internet",
    "Payouts",
    "SignedAgreement",
]


class CapabilityRequestCreateParams(TypedDict, total=False):
    businesses: Businesses
    """Allows the account to accept payments from businesses."""

    charges: Charges
    """The charges capability settings for the account."""

    individuals: Individuals
    """Allows the account to accept payments from individuals."""

    internet: Internet
    """
    Allows the account to accept payments authorized via the internet or mobile
    applications.
    """

    payouts: Payouts
    """The payouts capability settings for the account."""

    signed_agreement: SignedAgreement
    """
    Allows the account to accept payments authorized by signed agreements or
    contracts.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]


class Businesses(TypedDict, total=False):
    enable: Required[bool]


class Charges(TypedDict, total=False):
    daily_amount: Required[float]
    """The maximum dollar amount of charges in a calendar day."""

    enable: Required[bool]
    """Determines whether `charges` are enabled for the account."""

    max_amount: Required[float]
    """The maximum amount of a single charge."""

    monthly_amount: Required[float]
    """The maximum dollar amount of charges in a calendar month."""

    monthly_count: Required[int]
    """The maximum number of charges in a calendar month."""


class Individuals(TypedDict, total=False):
    enable: Required[bool]


class Internet(TypedDict, total=False):
    enable: Required[bool]


class Payouts(TypedDict, total=False):
    daily_amount: Required[float]
    """The maximum dollar amount of payouts in a day."""

    enable: Required[bool]
    """Determines whether `payouts` are enabled for the account."""

    max_amount: Required[float]
    """The maximum amount of a single payout."""

    monthly_amount: Required[float]
    """The maximum dollar amount of payouts in a month."""

    monthly_count: Required[int]
    """The maximum number of payouts in a month."""


class SignedAgreement(TypedDict, total=False):
    enable: Required[bool]
