# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.device_info_v1 import DeviceInfoV1

__all__ = ["ChargeCreateParams", "Config"]


class ChargeCreateParams(TypedDict, total=False):
    amount: Required[int]
    """The amount of the charge in cents."""

    config: Required[Config]

    consent_type: Required[Literal["internet", "signed"]]
    """The channel or mechanism through which the payment was authorized.

    Use `internet` for payments made online or through a mobile app and `signed` for
    signed agreements where there is a consent form or contract. Use `signed` for
    PDF signatures.
    """

    currency: Required[str]
    """The currency of the charge. Only USD is supported."""

    description: Required[str]
    """An arbitrary description for the charge."""

    device: Required[DeviceInfoV1]

    external_id: Required[str]
    """Unique identifier for the charge in your database.

    This value must be unique across all charges.
    """

    paykey: Required[str]
    """Value of the `paykey` used for the charge."""

    payment_date: Required[Annotated[Union[str, date], PropertyInfo(format="iso8601")]]
    """The desired date on which the payment should be occur.

    For charges, this means the date you want the customer to be debited on.
    """

    metadata: Optional[Dict[str, str]]
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the charge in a structured
    format.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="Correlation-Id")]

    request_id: Annotated[str, PropertyInfo(alias="Request-Id")]

    straddle_account_id: Annotated[str, PropertyInfo(alias="Straddle-Account-Id")]


class Config(TypedDict, total=False):
    balance_check: Required[Literal["required", "enabled", "disabled"]]
    """Defines whether to check the customer's balance before processing the charge."""

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
