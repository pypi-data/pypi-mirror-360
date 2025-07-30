# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["SchoolRatingsResponse", "Result"]


class Result(BaseModel):
    address_token: str

    token: Optional[str] = None
    """The user-supplied token submitted for the address."""

    avg_ratings: Optional[float] = None
    """
    The average of the given property's schools' (elementary, middle, and high
    school) ratings.
    """

    elementary_name: Optional[str] = None
    """The property's elementary school's name."""

    elementary_rating: Optional[float] = None
    """The property's elementary school's rating."""

    error_message: Optional[str] = None
    """The error message if the system was unable to process this address."""

    high_name: Optional[str] = None
    """The property's high school's name."""

    high_rating: Optional[float] = None
    """The property's high school's rating."""

    middle_name: Optional[str] = None
    """The property's middle school's name."""

    middle_rating: Optional[float] = None
    """The property's middle school's rating."""


class SchoolRatingsResponse(BaseModel):
    results: List[Result]
    """The list of school ratings for each address."""
