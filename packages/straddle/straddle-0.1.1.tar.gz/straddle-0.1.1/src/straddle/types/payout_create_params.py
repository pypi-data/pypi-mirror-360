# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.device_info_v1 import DeviceInfoV1

__all__ = ["PayoutCreateParams", "Config"]


class PayoutCreateParams(TypedDict, total=False):
    amount: Required[int]
    """The amount of the payout in cents."""

    currency: Required[str]
    """The currency of the payout. Only USD is supported."""

    description: Required[str]
    """An arbitrary description for the payout."""

    device: Required[DeviceInfoV1]
    """Information about the device used when the customer authorized the payout."""

    external_id: Required[str]
    """Unique identifier for the payout in your database.

    This value must be unique across all payouts.
    """

    paykey: Required[str]
    """Value of the `paykey` used for the payout."""

    payment_date: Required[Annotated[Union[str, date], PropertyInfo(format="iso8601")]]
    """The desired date on which the payout should be occur.

    For payouts, this means the date you want the funds to be sent from your bank
    account.
    """

    config: Config

    metadata: Optional[Dict[str, str]]
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the payout in a structured
    format.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="Correlation-Id")]

    request_id: Annotated[str, PropertyInfo(alias="Request-Id")]

    straddle_account_id: Annotated[str, PropertyInfo(alias="Straddle-Account-Id")]


class Config(TypedDict, total=False):
    sandbox_outcome: Literal[
        "standard",
        "paid",
        "on_hold_daily_limit",
        "cancelled_for_fraud_risk",
        "cancelled_for_balance_check",
        "failed_insufficient_funds",
        "reversed_insufficient_funds",
        "failed_customer_dispute",
        "reversed_customer_dispute",
        "failed_closed_bank_account",
        "reversed_closed_bank_account",
    ]
    """Payment will simulate processing if not Standard."""
