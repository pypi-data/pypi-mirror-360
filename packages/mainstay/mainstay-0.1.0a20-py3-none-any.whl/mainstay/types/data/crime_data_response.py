# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["CrimeDataResponse", "Result"]


class Result(BaseModel):
    address_token: str

    token: Optional[str] = None
    """The user-supplied token submitted for the address."""

    county_percentile: Optional[float] = None
    """
    The percentile rank within the county for the number of crime incidents near the
    block of the property.
    """

    error_message: Optional[str] = None
    """The error message if the system was unable to process this address."""

    nation_percentile: Optional[float] = None
    """
    The percentile rank within the US for the number of crime incidents near the
    block of the property.
    """


class CrimeDataResponse(BaseModel):
    results: List[Result]
    """The list of crime data for each address."""
