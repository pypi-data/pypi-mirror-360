# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["PaykeyDetailsV1"]


class PaykeyDetailsV1(BaseModel):
    id: str
    """Unique identifier for the paykey."""

    customer_id: str
    """Unique identifier for the customer associated with the paykey."""

    label: str
    """
    Human-readable label that combines the bank name and masked account number to
    help easility represent this paykey in a UI
    """

    balance: Optional[int] = None
    """
    The most recent balance of the bank account associated with the paykey in
    dollars.
    """
