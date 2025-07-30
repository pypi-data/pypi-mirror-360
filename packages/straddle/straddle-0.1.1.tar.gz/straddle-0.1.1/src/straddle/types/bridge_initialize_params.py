# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BridgeInitializeParams", "Config"]


class BridgeInitializeParams(TypedDict, total=False):
    customer_id: Required[str]
    """
    The Straddle generated unique identifier of the `customer` to create a bridge
    token for.
    """

    config: Config

    correlation_id: Annotated[str, PropertyInfo(alias="Correlation-Id")]

    request_id: Annotated[str, PropertyInfo(alias="Request-Id")]

    straddle_account_id: Annotated[str, PropertyInfo(alias="Straddle-Account-Id")]


class Config(TypedDict, total=False):
    sandbox_outcome: Literal["standard", "active", "rejected"]
