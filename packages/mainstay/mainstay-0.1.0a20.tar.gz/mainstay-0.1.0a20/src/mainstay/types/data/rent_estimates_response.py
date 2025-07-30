# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["RentEstimatesResponse", "Result", "ResultRentEstimate"]


class ResultRentEstimate(BaseModel):
    estimated_rent: int
    """The estimated rent for the address."""

    estimated_rent_high: int
    """The upper bound of the estimated rent range."""

    estimated_rent_low: int
    """The lower bound of the estimated rent range."""


class Result(BaseModel):
    token: Optional[str] = None
    """The user-supplied token submitted for the address."""

    rent_estimate: Optional[ResultRentEstimate] = None
    """The rent estimate for the address."""


class RentEstimatesResponse(BaseModel):
    results: List[Result]
    """The list of rent estimates for each address."""
