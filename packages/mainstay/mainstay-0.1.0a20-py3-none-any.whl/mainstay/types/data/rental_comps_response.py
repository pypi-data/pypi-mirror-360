# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = [
    "RentalCompsResponse",
    "Result",
    "ResultRentalComps",
    "ResultRentalCompsPropertyDetails",
    "ResultSubjectPropertyDetails",
]


class ResultRentalCompsPropertyDetails(BaseModel):
    city: str
    """The city name where the property resides."""

    postal_code: str
    """The 5 digit zip or postal code of the location where the property resides."""

    state: str
    """The state abbreviation where the property resides (e.g. `"CA"`)."""

    street: str
    """
    The full street address where the property resides, including the street number
    and street name.
    """

    above_grade_sqft: Optional[int] = None
    """The living_area_sqft - basement_sqft or `null`"""

    basement_sqft: Optional[int] = None
    """The approximate square footage of the basement."""

    bathrooms_full: Optional[int] = None
    """The number of full baths, capped at 5.

    A full bath contains all 4 of the 4 elements constituting a bath: Toilet, Sink,
    Bathtub, or Shower Head. A Full Bath will typically contain four elements; Sink,
    Toilet, Tub, and Shower Head (in tub or stall).
    """

    bathrooms_half: Optional[int] = None
    """The number of half baths. A half bath contains a Toilet and a Sink"""

    bedrooms_total: Optional[int] = None
    """The number of bedrooms, capped at 5."""

    garage_spaces: Optional[int] = None
    """The number of spaces in the garage(s)."""

    has_private_pool: Optional[bool] = None
    """
    TRUE if the property has a privately owned pool that is included in the
    sale/lease.
    """

    is_btr: Optional[bool] = None
    """TRUE if the property is part of a build to rent.

    Build To Rent (BTR) is a type of planned community where the developer plans on
    renting all or a substantial section of a subdivision. Not set if unknown.
    """

    is_in_hoa: Optional[bool] = None
    """TRUE if the property is inside a hoa. Not set if unknown."""

    latitude: Optional[float] = None
    """The approximate latitude of the property."""

    living_area_sqft: Optional[int] = None
    """The approximate livable area within the structure, designated in Square Feet."""

    longitude: Optional[float] = None
    """The approximate longitude of the property."""

    lot_size_sqft: Optional[int] = None
    """The total square footage of the lot."""

    msa_name: Optional[str] = None
    """The property's Metropolitan Statistical Area (MSA) name.

    Not set if property is not in a Metropolitan Statistical Area.
    """

    num_exterior_stories: Optional[int] = None
    """The number of above ground stories on the property."""

    ownership_profile: Optional[str] = None
    """The property owner's estimated portfolio size.

    The output can be one of the following: "<100", "100-1k", "1k-20k", "20k+".
    """

    slug: Optional[str] = None
    """A URL-safe string identifying the property address.

    The slug may be used in Rental Advisor URLs (e.g.
    https://marketadvisor.mainstay.io/address/{slug}).
    """

    structure_type: Optional[str] = None
    """The type of structure that the property completely or partially encompasses.

    For example, House or Cabin are the overall structure and typically sold or
    leased as a whole. Multi Family and Docks may be sold in whole, but are often
    sold or leased by unit/slip. This field is the type of structure as opposed to
    style, which is under the Architectural Style field.
    """

    subdivision_name: Optional[str] = None
    """The name of the subdivision where the property is located."""

    unit: Optional[str] = None
    """The unit type and number of the property (e.g. `"Apt 123"`)."""

    year_built: Optional[int] = None
    """The year the property was built, rounded to the nearest 5."""


class ResultRentalComps(BaseModel):
    close_price: Optional[int] = None
    """
    The approximate last known closed monthly rental price for the property,
    denominated in dollars and cents.
    """

    close_price_date: Optional[date] = None
    """
    The approximate earliest known calendar day on which the closed rent became
    effective.
    """

    concession_description: Optional[str] = None
    """Description of any concessions available for the property."""

    concession_end_date: Optional[date] = None
    """End date of the concession period."""

    concession_start_date: Optional[date] = None
    """Start date of the concession period."""

    distance_miles: Optional[float] = None
    """The distance in miles from the subject property to the comp."""

    dom: Optional[int] = None
    """Days on Market for this property."""

    initial_list_price: Optional[int] = None
    """The initial list price of the property."""

    initial_list_price_date: Optional[date] = None
    """
    The approximate first known date at which the listed rent was publicly displayed
    or updated.
    """

    last_event_date: Optional[date] = None
    """The date which the last listing event occurred.

    This usually means a change in `listing_status`.
    """

    last_list_price: Optional[int] = None
    """
    The approximate last known published list rent for the property, denominated in
    dollars and cents.
    """

    listing_description: Optional[str] = None
    """Complete listing description as mentioned on the listing source website."""

    listing_status: Optional[Literal["active", "removed", "closed"]] = None
    """
    The status of the property: `active` refers to properties that are currently
    available for
    rent."closed"`refers to properties that were previously available for rent but have since been rented out.`removed`
    indicates that the listing associated with this property is no longer active.
    """

    move_out_date: Optional[date] = None
    """
    The date when the tenant moved out from the leased property during the previous
    lease.
    """

    ownership_profile: Optional[str] = None

    property_details: Optional[ResultRentalCompsPropertyDetails] = None
    """The property details for the comp."""

    response_codes: Optional[List[str]] = None
    """A list containing information about this comp subject property pairing.

    The possible response codes are as following:

    - estimated_close_price: the comp's listing has closed, but the actual close
      price is not yet known. In this case, the last list price is used as an
      estimate. close_price will be equal to the last known list_price
    """

    similarity_score: Optional[float] = None
    """
    A score between 0 and 1 describing how similar this comp is to the subject
    property. Similarity accounts for both home details (bed, bath, year built,
    etc.) as well as location. A larger score indicates a more similar comp.
    """


class ResultSubjectPropertyDetails(BaseModel):
    city: str
    """The city name where the property resides."""

    postal_code: str
    """The 5 digit zip or postal code of the location where the property resides."""

    state: str
    """The state abbreviation where the property resides (e.g. `"CA"`)."""

    street: str
    """
    The full street address where the property resides, including the street number
    and street name.
    """

    above_grade_sqft: Optional[int] = None
    """The living_area_sqft - basement_sqft or `null`"""

    basement_sqft: Optional[int] = None
    """The approximate square footage of the basement."""

    bathrooms_full: Optional[int] = None
    """The number of full baths, capped at 5.

    A full bath contains all 4 of the 4 elements constituting a bath: Toilet, Sink,
    Bathtub, or Shower Head. A Full Bath will typically contain four elements; Sink,
    Toilet, Tub, and Shower Head (in tub or stall).
    """

    bathrooms_half: Optional[int] = None
    """The number of half baths. A half bath contains a Toilet and a Sink"""

    bedrooms_total: Optional[int] = None
    """The number of bedrooms, capped at 5."""

    garage_spaces: Optional[int] = None
    """The number of spaces in the garage(s)."""

    has_private_pool: Optional[bool] = None
    """
    TRUE if the property has a privately owned pool that is included in the
    sale/lease.
    """

    is_btr: Optional[bool] = None
    """TRUE if the property is part of a build to rent.

    Build To Rent (BTR) is a type of planned community where the developer plans on
    renting all or a substantial section of a subdivision. Not set if unknown.
    """

    is_in_hoa: Optional[bool] = None
    """TRUE if the property is inside a hoa. Not set if unknown."""

    latitude: Optional[float] = None
    """The approximate latitude of the property."""

    living_area_sqft: Optional[int] = None
    """The approximate livable area within the structure, designated in Square Feet."""

    longitude: Optional[float] = None
    """The approximate longitude of the property."""

    lot_size_sqft: Optional[int] = None
    """The total square footage of the lot."""

    msa_name: Optional[str] = None
    """The property's Metropolitan Statistical Area (MSA) name.

    Not set if property is not in a Metropolitan Statistical Area.
    """

    num_exterior_stories: Optional[int] = None
    """The number of above ground stories on the property."""

    ownership_profile: Optional[str] = None
    """The property owner's estimated portfolio size.

    The output can be one of the following: "<100", "100-1k", "1k-20k", "20k+".
    """

    slug: Optional[str] = None
    """A URL-safe string identifying the property address.

    The slug may be used in Rental Advisor URLs (e.g.
    https://marketadvisor.mainstay.io/address/{slug}).
    """

    structure_type: Optional[str] = None
    """The type of structure that the property completely or partially encompasses.

    For example, House or Cabin are the overall structure and typically sold or
    leased as a whole. Multi Family and Docks may be sold in whole, but are often
    sold or leased by unit/slip. This field is the type of structure as opposed to
    style, which is under the Architectural Style field.
    """

    subdivision_name: Optional[str] = None
    """The name of the subdivision where the property is located."""

    unit: Optional[str] = None
    """The unit type and number of the property (e.g. `"Apt 123"`)."""

    year_built: Optional[int] = None
    """The year the property was built, rounded to the nearest 5."""


class Result(BaseModel):
    api_code: int
    """An HTTP status code indicating the result of the address request."""

    rental_comps: List[ResultRentalComps]
    """The list of rental comps for the address."""

    token: Optional[str] = None
    """The user-supplied token submitted for the address."""

    error_message: Optional[str] = None
    """The error message if the system was unable to process this address."""

    has_errors: Optional[bool] = None
    """Boolean indicating if the system was unable to process this address.

    DEPRECATED: Use `api_code` instead.
    """

    subject_property_details: Optional[ResultSubjectPropertyDetails] = None
    """The property details for the address."""


class RentalCompsResponse(BaseModel):
    results: List[Result]
    """The list of rental comps for each address."""
