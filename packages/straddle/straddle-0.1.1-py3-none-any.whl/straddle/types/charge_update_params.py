# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from datetime import date
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ChargeUpdateParams"]


class ChargeUpdateParams(TypedDict, total=False):
    amount: Required[int]
    """The amount of the charge in cents."""

    description: Required[str]
    """An arbitrary description for the charge."""

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
