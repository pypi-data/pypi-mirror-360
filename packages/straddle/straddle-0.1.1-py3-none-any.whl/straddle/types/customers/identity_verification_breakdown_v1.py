# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["IdentityVerificationBreakdownV1"]


class IdentityVerificationBreakdownV1(BaseModel):
    codes: Optional[List[str]] = None
    """List of specific result codes from the fraud and risk screening."""

    correlation: Optional[Literal["low_confidence", "potential_match", "likely_match", "high_confidence"]] = None

    correlation_score: Optional[float] = None
    """
    Represents the strength of the correlation between provided and known
    information. A higher score indicates a stronger correlation.
    """

    decision: Optional[Literal["accept", "reject", "review"]] = None

    risk_score: Optional[float] = None
    """Predicts the inherent risk associated with the customer for a given module.

    A higher score indicates a greater likelihood of fraud.
    """
