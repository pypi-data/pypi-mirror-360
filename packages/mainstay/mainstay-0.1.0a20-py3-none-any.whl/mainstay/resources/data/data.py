# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from .crime_data import (
    CrimeDataResource,
    AsyncCrimeDataResource,
    CrimeDataResourceWithRawResponse,
    AsyncCrimeDataResourceWithRawResponse,
    CrimeDataResourceWithStreamingResponse,
    AsyncCrimeDataResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from .rental_comps import (
    RentalCompsResource,
    AsyncRentalCompsResource,
    RentalCompsResourceWithRawResponse,
    AsyncRentalCompsResourceWithRawResponse,
    RentalCompsResourceWithStreamingResponse,
    AsyncRentalCompsResourceWithStreamingResponse,
)
from .rent_estimates import (
    RentEstimatesResource,
    AsyncRentEstimatesResource,
    RentEstimatesResourceWithRawResponse,
    AsyncRentEstimatesResourceWithRawResponse,
    RentEstimatesResourceWithStreamingResponse,
    AsyncRentEstimatesResourceWithStreamingResponse,
)
from .school_ratings import (
    SchoolRatingsResource,
    AsyncSchoolRatingsResource,
    SchoolRatingsResourceWithRawResponse,
    AsyncSchoolRatingsResourceWithRawResponse,
    SchoolRatingsResourceWithStreamingResponse,
    AsyncSchoolRatingsResourceWithStreamingResponse,
)
from .property_values import (
    PropertyValuesResource,
    AsyncPropertyValuesResource,
    PropertyValuesResourceWithRawResponse,
    AsyncPropertyValuesResourceWithRawResponse,
    PropertyValuesResourceWithStreamingResponse,
    AsyncPropertyValuesResourceWithStreamingResponse,
)
from .property_details import (
    PropertyDetailsResource,
    AsyncPropertyDetailsResource,
    PropertyDetailsResourceWithRawResponse,
    AsyncPropertyDetailsResourceWithRawResponse,
    PropertyDetailsResourceWithStreamingResponse,
    AsyncPropertyDetailsResourceWithStreamingResponse,
)

__all__ = ["DataResource", "AsyncDataResource"]


class DataResource(SyncAPIResource):
    @cached_property
    def property_details(self) -> PropertyDetailsResource:
        return PropertyDetailsResource(self._client)

    @cached_property
    def property_values(self) -> PropertyValuesResource:
        return PropertyValuesResource(self._client)

    @cached_property
    def rent_estimates(self) -> RentEstimatesResource:
        return RentEstimatesResource(self._client)

    @cached_property
    def rental_comps(self) -> RentalCompsResource:
        return RentalCompsResource(self._client)

    @cached_property
    def crime_data(self) -> CrimeDataResource:
        return CrimeDataResource(self._client)

    @cached_property
    def school_ratings(self) -> SchoolRatingsResource:
        return SchoolRatingsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DataResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#accessing-raw-response-data-eg-headers
        """
        return DataResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DataResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#with_streaming_response
        """
        return DataResourceWithStreamingResponse(self)


class AsyncDataResource(AsyncAPIResource):
    @cached_property
    def property_details(self) -> AsyncPropertyDetailsResource:
        return AsyncPropertyDetailsResource(self._client)

    @cached_property
    def property_values(self) -> AsyncPropertyValuesResource:
        return AsyncPropertyValuesResource(self._client)

    @cached_property
    def rent_estimates(self) -> AsyncRentEstimatesResource:
        return AsyncRentEstimatesResource(self._client)

    @cached_property
    def rental_comps(self) -> AsyncRentalCompsResource:
        return AsyncRentalCompsResource(self._client)

    @cached_property
    def crime_data(self) -> AsyncCrimeDataResource:
        return AsyncCrimeDataResource(self._client)

    @cached_property
    def school_ratings(self) -> AsyncSchoolRatingsResource:
        return AsyncSchoolRatingsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDataResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDataResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDataResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#with_streaming_response
        """
        return AsyncDataResourceWithStreamingResponse(self)


class DataResourceWithRawResponse:
    def __init__(self, data: DataResource) -> None:
        self._data = data

    @cached_property
    def property_details(self) -> PropertyDetailsResourceWithRawResponse:
        return PropertyDetailsResourceWithRawResponse(self._data.property_details)

    @cached_property
    def property_values(self) -> PropertyValuesResourceWithRawResponse:
        return PropertyValuesResourceWithRawResponse(self._data.property_values)

    @cached_property
    def rent_estimates(self) -> RentEstimatesResourceWithRawResponse:
        return RentEstimatesResourceWithRawResponse(self._data.rent_estimates)

    @cached_property
    def rental_comps(self) -> RentalCompsResourceWithRawResponse:
        return RentalCompsResourceWithRawResponse(self._data.rental_comps)

    @cached_property
    def crime_data(self) -> CrimeDataResourceWithRawResponse:
        return CrimeDataResourceWithRawResponse(self._data.crime_data)

    @cached_property
    def school_ratings(self) -> SchoolRatingsResourceWithRawResponse:
        return SchoolRatingsResourceWithRawResponse(self._data.school_ratings)


class AsyncDataResourceWithRawResponse:
    def __init__(self, data: AsyncDataResource) -> None:
        self._data = data

    @cached_property
    def property_details(self) -> AsyncPropertyDetailsResourceWithRawResponse:
        return AsyncPropertyDetailsResourceWithRawResponse(self._data.property_details)

    @cached_property
    def property_values(self) -> AsyncPropertyValuesResourceWithRawResponse:
        return AsyncPropertyValuesResourceWithRawResponse(self._data.property_values)

    @cached_property
    def rent_estimates(self) -> AsyncRentEstimatesResourceWithRawResponse:
        return AsyncRentEstimatesResourceWithRawResponse(self._data.rent_estimates)

    @cached_property
    def rental_comps(self) -> AsyncRentalCompsResourceWithRawResponse:
        return AsyncRentalCompsResourceWithRawResponse(self._data.rental_comps)

    @cached_property
    def crime_data(self) -> AsyncCrimeDataResourceWithRawResponse:
        return AsyncCrimeDataResourceWithRawResponse(self._data.crime_data)

    @cached_property
    def school_ratings(self) -> AsyncSchoolRatingsResourceWithRawResponse:
        return AsyncSchoolRatingsResourceWithRawResponse(self._data.school_ratings)


class DataResourceWithStreamingResponse:
    def __init__(self, data: DataResource) -> None:
        self._data = data

    @cached_property
    def property_details(self) -> PropertyDetailsResourceWithStreamingResponse:
        return PropertyDetailsResourceWithStreamingResponse(self._data.property_details)

    @cached_property
    def property_values(self) -> PropertyValuesResourceWithStreamingResponse:
        return PropertyValuesResourceWithStreamingResponse(self._data.property_values)

    @cached_property
    def rent_estimates(self) -> RentEstimatesResourceWithStreamingResponse:
        return RentEstimatesResourceWithStreamingResponse(self._data.rent_estimates)

    @cached_property
    def rental_comps(self) -> RentalCompsResourceWithStreamingResponse:
        return RentalCompsResourceWithStreamingResponse(self._data.rental_comps)

    @cached_property
    def crime_data(self) -> CrimeDataResourceWithStreamingResponse:
        return CrimeDataResourceWithStreamingResponse(self._data.crime_data)

    @cached_property
    def school_ratings(self) -> SchoolRatingsResourceWithStreamingResponse:
        return SchoolRatingsResourceWithStreamingResponse(self._data.school_ratings)


class AsyncDataResourceWithStreamingResponse:
    def __init__(self, data: AsyncDataResource) -> None:
        self._data = data

    @cached_property
    def property_details(self) -> AsyncPropertyDetailsResourceWithStreamingResponse:
        return AsyncPropertyDetailsResourceWithStreamingResponse(self._data.property_details)

    @cached_property
    def property_values(self) -> AsyncPropertyValuesResourceWithStreamingResponse:
        return AsyncPropertyValuesResourceWithStreamingResponse(self._data.property_values)

    @cached_property
    def rent_estimates(self) -> AsyncRentEstimatesResourceWithStreamingResponse:
        return AsyncRentEstimatesResourceWithStreamingResponse(self._data.rent_estimates)

    @cached_property
    def rental_comps(self) -> AsyncRentalCompsResourceWithStreamingResponse:
        return AsyncRentalCompsResourceWithStreamingResponse(self._data.rental_comps)

    @cached_property
    def crime_data(self) -> AsyncCrimeDataResourceWithStreamingResponse:
        return AsyncCrimeDataResourceWithStreamingResponse(self._data.crime_data)

    @cached_property
    def school_ratings(self) -> AsyncSchoolRatingsResourceWithStreamingResponse:
        return AsyncSchoolRatingsResourceWithStreamingResponse(self._data.school_ratings)
