# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .terms_of_service_v1_param import TermsOfServiceV1Param

__all__ = ["AccountOnboardParams"]


class AccountOnboardParams(TypedDict, total=False):
    terms_of_service: Required[TermsOfServiceV1Param]

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]
