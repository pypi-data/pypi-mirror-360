# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "RentalCompsFetchParams",
    "Address",
    "Filters",
    "FiltersBathroomsFull",
    "FiltersBathroomsFullFilterByNumericRange",
    "FiltersBathroomsFullFilterRelativeNumeric",
    "FiltersBathroomsHalf",
    "FiltersBathroomsHalfFilterByNumericRange",
    "FiltersBathroomsHalfFilterRelativeNumeric",
    "FiltersBaths",
    "FiltersBathsFilterByNumericRange",
    "FiltersBathsFilterRelativeNumeric",
    "FiltersBedroomsTotal",
    "FiltersBedroomsTotalFilterByNumericRange",
    "FiltersBedroomsTotalFilterRelativeNumeric",
    "FiltersBeds",
    "FiltersBedsFilterByNumericRange",
    "FiltersBedsFilterRelativeNumeric",
    "FiltersDate",
    "FiltersDateFilterByDateRange",
    "FiltersDateFilterRelativeNumeric",
    "FiltersLivingAreaSqft",
    "FiltersLivingAreaSqftFilterByNumericRange",
    "FiltersLivingAreaSqftFilterRelativeNumeric",
    "FiltersYearBuilt",
    "FiltersYearBuiltFilterByNumericRange",
    "FiltersYearBuiltFilterRelativeNumeric",
]


class RentalCompsFetchParams(TypedDict, total=False):
    addresses: Required[Iterable[Address]]
    """An array of address objects, each specifying a property location."""

    filters: Optional[Filters]
    """
    An _optional_ object containing criteria to refine the rental comps search, such
    as date range, price, number of bedrooms, etc. If no filters are provided, the
    search will include all available comps.
    """

    num_comps: int
    """
    An _optional_ int containing the number of rental comps to return per subject
    address. The minimum value is 1 and the maximum value is 50. If no value is
    provided, we will return our top 10 comps.
    """


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


class FiltersBathroomsFullFilterByNumericRange(TypedDict, total=False):
    max: int
    """The maximum value of the range."""

    min: int
    """The minimum value of the range."""


class FiltersBathroomsFullFilterRelativeNumeric(TypedDict, total=False):
    relative: int
    """The relative value to use for the filter.

    For example, if the value is `10`, the filter will use the value of the subject
    property and filter by +/- `10` of that value.
    """


FiltersBathroomsFull: TypeAlias = Union[
    FiltersBathroomsFullFilterByNumericRange, FiltersBathroomsFullFilterRelativeNumeric
]


class FiltersBathroomsHalfFilterByNumericRange(TypedDict, total=False):
    max: int
    """The maximum value of the range."""

    min: int
    """The minimum value of the range."""


class FiltersBathroomsHalfFilterRelativeNumeric(TypedDict, total=False):
    relative: int
    """The relative value to use for the filter.

    For example, if the value is `10`, the filter will use the value of the subject
    property and filter by +/- `10` of that value.
    """


FiltersBathroomsHalf: TypeAlias = Union[
    FiltersBathroomsHalfFilterByNumericRange, FiltersBathroomsHalfFilterRelativeNumeric
]


class FiltersBathsFilterByNumericRange(TypedDict, total=False):
    max: int
    """The maximum value of the range."""

    min: int
    """The minimum value of the range."""


class FiltersBathsFilterRelativeNumeric(TypedDict, total=False):
    relative: int
    """The relative value to use for the filter.

    For example, if the value is `10`, the filter will use the value of the subject
    property and filter by +/- `10` of that value.
    """


FiltersBaths: TypeAlias = Union[FiltersBathsFilterByNumericRange, FiltersBathsFilterRelativeNumeric]


class FiltersBedroomsTotalFilterByNumericRange(TypedDict, total=False):
    max: int
    """The maximum value of the range."""

    min: int
    """The minimum value of the range."""


class FiltersBedroomsTotalFilterRelativeNumeric(TypedDict, total=False):
    relative: int
    """The relative value to use for the filter.

    For example, if the value is `10`, the filter will use the value of the subject
    property and filter by +/- `10` of that value.
    """


FiltersBedroomsTotal: TypeAlias = Union[
    FiltersBedroomsTotalFilterByNumericRange, FiltersBedroomsTotalFilterRelativeNumeric
]


class FiltersBedsFilterByNumericRange(TypedDict, total=False):
    max: int
    """The maximum value of the range."""

    min: int
    """The minimum value of the range."""


class FiltersBedsFilterRelativeNumeric(TypedDict, total=False):
    relative: int
    """The relative value to use for the filter.

    For example, if the value is `10`, the filter will use the value of the subject
    property and filter by +/- `10` of that value.
    """


FiltersBeds: TypeAlias = Union[FiltersBedsFilterByNumericRange, FiltersBedsFilterRelativeNumeric]


class FiltersDateFilterByDateRange(TypedDict, total=False):
    max: Required[Annotated[Union[str, date], PropertyInfo(format="iso8601")]]
    """The maximum date of the range."""

    min: Required[Annotated[Union[str, date], PropertyInfo(format="iso8601")]]
    """The minimum date of the range."""


class FiltersDateFilterRelativeNumeric(TypedDict, total=False):
    relative: int
    """The relative value to use for the filter.

    For example, if the value is `10`, the filter will use the value of the subject
    property and filter by +/- `10` of that value.
    """


FiltersDate: TypeAlias = Union[FiltersDateFilterByDateRange, FiltersDateFilterRelativeNumeric]


class FiltersLivingAreaSqftFilterByNumericRange(TypedDict, total=False):
    max: int
    """The maximum value of the range."""

    min: int
    """The minimum value of the range."""


class FiltersLivingAreaSqftFilterRelativeNumeric(TypedDict, total=False):
    relative: int
    """The relative value to use for the filter.

    For example, if the value is `10`, the filter will use the value of the subject
    property and filter by +/- `10` of that value.
    """


FiltersLivingAreaSqft: TypeAlias = Union[
    FiltersLivingAreaSqftFilterByNumericRange, FiltersLivingAreaSqftFilterRelativeNumeric
]


class FiltersYearBuiltFilterByNumericRange(TypedDict, total=False):
    max: int
    """The maximum value of the range."""

    min: int
    """The minimum value of the range."""


class FiltersYearBuiltFilterRelativeNumeric(TypedDict, total=False):
    relative: int
    """The relative value to use for the filter.

    For example, if the value is `10`, the filter will use the value of the subject
    property and filter by +/- `10` of that value.
    """


FiltersYearBuilt: TypeAlias = Union[FiltersYearBuiltFilterByNumericRange, FiltersYearBuiltFilterRelativeNumeric]


class Filters(TypedDict, total=False):
    bathrooms_full: Optional[FiltersBathroomsFull]
    """This field is replacing `baths`.

    When the **`FilterRelativeNumeric`** is used, only comps which have a number of
    full bathrooms that are within the provided `value` of the supplied address. For
    example, providing a value of `2` for an address that has `3` full bathrooms
    will return comps that have between (inclusive) `3+2 = 5` and `3-2 = 1` full
    bathrooms.

    When the **`FilterByNumericRange`** is used, only comps with a number of full
    bathrooms that fit within the supplied minimum (inclusive) and maximum value
    (inclusive).
    """

    bathrooms_half: Optional[FiltersBathroomsHalf]
    """
    When the **`FilterRelativeNumeric`** is used, only comps which have a number of
    half bathrooms that are within the provided `value` of the supplied address. For
    example, providing a value of `1` for an address that has `2` half bathrooms
    will return comps that have between (inclusive) `2+1 = 3` and `2-1 = 1` half
    bathrooms.

    When the **`FilterByNumericRange`** is used, only comps with a number of half
    bathrooms that fit within the supplied minimum (inclusive) and maximum value
    (inclusive).
    """

    baths: Optional[FiltersBaths]
    """This field is being replaced by `bathrooms_full`.

    Please use `bathrooms_full` instead. Using this field will raise a 422 exception
    and ask you to use `bathrooms_full`. When the **`FilterRelativeNumeric`** is
    used, only comps which have a number offull bathrooms that are within the
    provided `value` of the supplied address. For example, providing a value of `2`
    for an address that has `3` full bathrooms will return comps that have between
    (inclusive) `3+2 = 5` and `3-2 = 1` full bathrooms.

    When the **`FilterByNumericRange`** is used, only comps with a number of full
    bathrooms that fit within the supplied minimum (inclusive) and maximum value
    (inclusive).
    """

    bedrooms_total: Optional[FiltersBedroomsTotal]
    """This field is replacing `beds`.

    When the **`FilterRelativeNumeric`** is used, only comps which have a number of
    bedroomsthat are within the provided `value` of the supplied address. For
    example, providing a `value` of `1` for an address that has `2` bedrooms will
    return only comps that have between (inclusive) `2+1 = 3` and `2-1 = 1`
    bedrooms.

    When the **`FilterByNumericRange`** is used, only comps with a number of
    bedrooms that fit within the supplied minimum (inclusive) and maximum value
    (inclusive).
    """

    beds: Optional[FiltersBeds]
    """This field is being replaced by `bedrooms_total`.

    Please use `bedrooms_total` instead. Any value set here will override the
    **`bedrooms_total`** field. When the **`FilterRelativeNumeric`** is used, only
    comps which have a number of bedroomsthat are within the provided `value` of the
    supplied address. For example, providing a `value` of `1` for an address that
    has `2` bedrooms will return only comps that have between (inclusive) `2+1 = 3`
    and `2-1 = 1` bedrooms.

    When the **`FilterByNumericRange`** is used, only comps with a number of
    bedrooms that fit within the supplied minimum (inclusive) and maximum value
    (inclusive).
    """

    date: Optional[FiltersDate]
    """
    When the **`FilterRelativeNumeric`** is used, only comps which have had their
    last listing event occur within past `value` days will be returned where `value`
    is the supplied integer of the filter.

    When the **`FilterByDateRange`** is used, only comps with listing events that
    occurred before the minimum and maximum date supplied will be returned.
    """

    distance: Optional[float]
    """The maximum distance of the rental comp from the requested address.

    If no distance filter was provided, a default value of 2 will be used. This
    distance value provided must be greater than 0 and less than or equal to 25.
    """

    living_area_sqft: Optional[FiltersLivingAreaSqft]
    """
    When the **`FilterRelativeNumeric`** is used, only comps which have a square
    footage that is within the provided percentage `value` of the supplied address.
    For example, providing a value of `20` for an address that has `2500` square
    feet will return comps that have between (inclusive) `3000` and `2000` square
    feet as we look at +/- `20%` of the subject property square footage rounded to
    the nearest square foot.

    When the **`FilterByNumericRange`** is used, only comps with a square footage
    that fits within the supplied minimum (inclusive) and maximum value (inclusive).
    """

    min_similarity_score: Optional[float]
    """
    Lower bound for the similarity score filter for nearby properties to be
    considered as comps. Float within the range from 0 (Least similar) to 1 (Most
    similar).
    """

    ownership_profiles: List[Literal["<100", "100-1k", "1k-20k", "20k+"]]
    """
    Only comps with ownership profiles that match at least one of the Ownership
    Profiles within the list supplied will be returned. If this filter is used,
    properties for which we do not have ownership profile information for (response
    would have a null ownership profile) will be excluded from the results.
    """

    statuses: List[Literal["active", "removed", "closed"]]
    """
    Only comps with statuses that match at least one of the statuses within the list
    supplied will be returned.
    """

    structure_types: List[Literal["single_family", "multi_family", "townhouse"]]
    """
    Only comps with structure types that match at least one of the structure types
    within the list supplied will be returned. If this filter is used, properties
    for which we do not have structure type information for (response would have a
    null structure type) will be excluded from the results.
    """

    year_built: Optional[FiltersYearBuilt]
    """
    When the **`FilterRelativeNumeric`** is used, only comps which have a
    `year_built` within provided `value` years of the supplied address. For example,
    providing a value of `2` for an address that was built in `2019` square feet
    will return comps that were built between `2017` and `2021` as we look at +/-
    `2` years of the subject address.

    When the **`FilterByNumericRange`** is used, only comps built within the
    supplied minimum (inclusive) and maximum value (inclusive) years will be
    returned.
    """
