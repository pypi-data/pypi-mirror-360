# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .business_profile_v1_param import BusinessProfileV1Param

__all__ = ["AccountCreateParams"]


class AccountCreateParams(TypedDict, total=False):
    access_level: Required[Literal["standard", "managed"]]
    """The access level granted to the account.

    This is determined by your platform configuration. Use `standard` unless
    instructed otherwise by Straddle.
    """

    account_type: Required[Literal["business"]]
    """The type of account to be created. Currently, only `business` is supported."""

    business_profile: Required[BusinessProfileV1Param]

    organization_id: Required[str]
    """The unique identifier of the organization related to this account."""

    external_id: Optional[str]
    """
    Unique identifier for the account in your database, used for cross-referencing
    between Straddle and your systems.
    """

    metadata: Optional[Dict[str, Optional[str]]]
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the account in a structured
    format.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]
