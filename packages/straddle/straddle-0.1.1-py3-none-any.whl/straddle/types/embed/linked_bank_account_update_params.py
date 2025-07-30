# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LinkedBankAccountUpdateParams", "BankAccount"]


class LinkedBankAccountUpdateParams(TypedDict, total=False):
    bank_account: Required[BankAccount]

    metadata: Optional[Dict[str, Optional[str]]]
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the linked bank account in a
    structured format.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]


class BankAccount(TypedDict, total=False):
    account_holder: Required[str]
    """The name of the account holder as it appears on the bank account.

    Typically, this is the legal name of the business associated with the account.
    """

    account_number: Required[str]
    """The bank account number."""

    routing_number: Required[str]
    """The routing number of the bank account."""
