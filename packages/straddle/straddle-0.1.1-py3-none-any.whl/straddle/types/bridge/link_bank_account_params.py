# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LinkBankAccountParams", "Config"]


class LinkBankAccountParams(TypedDict, total=False):
    account_number: Required[str]
    """The bank account number."""

    account_type: Required[Literal["checking", "savings"]]

    customer_id: Required[str]
    """Unique identifier of the related customer object."""

    routing_number: Required[str]
    """The routing number of the bank account."""

    config: Config

    metadata: Optional[Dict[str, str]]
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the paykey in a structured
    format.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="Correlation-Id")]

    request_id: Annotated[str, PropertyInfo(alias="Request-Id")]

    straddle_account_id: Annotated[str, PropertyInfo(alias="Straddle-Account-Id")]


class Config(TypedDict, total=False):
    sandbox_outcome: Literal["standard", "active", "rejected"]
