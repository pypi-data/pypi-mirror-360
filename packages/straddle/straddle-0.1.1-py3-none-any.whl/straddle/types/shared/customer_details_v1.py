# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["CustomerDetailsV1"]


class CustomerDetailsV1(BaseModel):
    id: str
    """Unique identifier for the customer"""

    customer_type: Literal["individual", "business"]
    """The type of customer"""

    email: str
    """The customer's email address"""

    name: str
    """The name of the customer"""

    phone: str
    """The customer's phone number in E.164 format"""
