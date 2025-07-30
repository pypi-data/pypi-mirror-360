# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["RentEstimatesFetchParams", "Address"]


class RentEstimatesFetchParams(TypedDict, total=False):
    addresses: Required[Iterable[Address]]
    """An array of address objects, each specifying a property location."""


class Address(TypedDict, total=False):
    city: Required[str]
    """The city name where the property resides."""

    postal_code: Required[str]
    """The 5 digit zip or postal code of the location where the property resides."""

    state: Required[str]
    """The state abbreviation where the property resides (e.g. `"CA"`)."""

    street: Required[str]
    """
    The full street address where the property resides, including the street number
    and street name.
    """

    token: Optional[str]
    """A user-defined token to help identify addresses in the response.

    The token which is provided in the request will always be returned in successful
    responses. This token is local to the request and does not persist across
    requests. This field is optional.
    """

    unit: Optional[str]
    """The unit type and number of the property (e.g. `"Apt 123"`)."""
