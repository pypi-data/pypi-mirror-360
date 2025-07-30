# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["DeviceInfoV1"]


class DeviceInfoV1(BaseModel):
    ip_address: str
    """
    The IP address of the device used when the customer authorized the charge or
    payout. Use `0.0.0.0` to represent an offline consent interaction.
    """
