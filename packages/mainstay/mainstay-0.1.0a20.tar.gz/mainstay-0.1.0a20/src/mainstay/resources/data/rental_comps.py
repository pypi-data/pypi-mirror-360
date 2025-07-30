# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import collections
import concurrent.futures.thread
from http import HTTPStatus
from typing import TYPE_CHECKING, Deque, Iterable, Optional

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.data import rental_comps_response, rental_comps_fetch_params
from ..._base_client import make_request_options
from ...types.data.rental_comps_response import RentalCompsResponse

if TYPE_CHECKING:
    from ... import Mainstay

__all__ = ["RentalCompsResource", "AsyncRentalCompsResource"]


MAX_CONCURRENT_REQUESTS = 4
MAX_ADDRESSES_PER_RENTAL_COMPS_REQUEST = 10
DEFAULT_RETRYABLE_STATUS_CODES = {
    HTTPStatus.BAD_GATEWAY,  # 502 status code
    HTTPStatus.GATEWAY_TIMEOUT,  # 504 status code
    HTTPStatus.SERVICE_UNAVAILABLE,  # 503 status code
}

class RentalCompsResource(SyncAPIResource):
    def __init__(self, client: Mainstay) -> None:
        super().__init__(client)
        self._executor = concurrent.futures.thread.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS)

    @cached_property
    def with_raw_response(self) -> RentalCompsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#accessing-raw-response-data-eg-headers
        """
        return RentalCompsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RentalCompsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#with_streaming_response
        """
        return RentalCompsResourceWithStreamingResponse(self)

    def fetch(
        self,
        *,
        addresses: Iterable[rental_comps_fetch_params.Address],
        filters: Optional[rental_comps_fetch_params.Filters] = None,
        num_comps: int | NotGiven = NOT_GIVEN,
        max_addresses_per_request: int = MAX_ADDRESSES_PER_RENTAL_COMPS_REQUEST,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Iterable[rental_comps_response.Result]:
        """
        Fetch rental comps for addresses (custom code)

        Args:
          addresses: An array of address objects, each specifying a property location.

          filters: An _optional_ object containing criteria to refine the rental comps search, such
              as date range, price, number of bedrooms, etc. If no filters are provided, the
              search will include all available comps.

          num_comps: An _optional_ int containing the number of rental comps to return per subject
              address. The minimum value is 1 and the maximum value is 50. If no value is
              provided, we will return our top 10 comps.

          max_addresses_per_request: The maximum number of addresses to include in each request.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        futures: Deque[concurrent.futures.Future[RentalCompsResponse]] = collections.deque()
        address_iter = iter(addresses)
        chunked_addresses_map: dict[concurrent.futures.Future[RentalCompsResponse], list[rental_comps_fetch_params.Address]] = {}

        def submit_request() -> None:
            chunked_addresses: list[rental_comps_fetch_params.Address] = []
            for address in address_iter:
                chunked_addresses.append(address)
                if len(chunked_addresses) >= max_addresses_per_request:
                    break
            if chunked_addresses:
                futures.append(
                    self._executor.submit(
                        self._fetch,
                        addresses=chunked_addresses,
                        filters=filters,
                        num_comps=num_comps,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout,
                    )
                )
                chunked_addresses_map[futures[-1]] = chunked_addresses

        # Submit initial requests. MAX_CONCURRENT_REQUESTS will be submitted and also queue up.
        for _ in range(MAX_CONCURRENT_REQUESTS * 2):
            submit_request()

        while futures:
            future = futures.popleft()
            results = future.result().results
            submit_request()

            # Retry any failed addresses from the chunk.
            if any(result.api_code in DEFAULT_RETRYABLE_STATUS_CODES for result in results):
                retry_addresses: list[rental_comps_fetch_params.Address] = []
                retry_indices: list[int] = []
                chunk_addresses = chunked_addresses_map[future]
                for idx, (result, address_to_retry) in enumerate(zip(results, chunk_addresses)):
                    if result.api_code not in DEFAULT_RETRYABLE_STATUS_CODES:
                        continue
                    retry_addresses.append(address_to_retry)
                    retry_indices.append(idx)
                retry_results = self._fetch(
                    addresses=retry_addresses,
                    filters=filters,
                    num_comps=num_comps,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                ).results
                for idx, result in zip(retry_indices, retry_results):
                    results[idx] = result

            yield from results

    def _fetch(
        self,
        *,
        addresses: Iterable[rental_comps_fetch_params.Address],
        filters: Optional[rental_comps_fetch_params.Filters] | NotGiven = NOT_GIVEN,
        num_comps: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RentalCompsResponse:
        """
        Fetch rental comps for addresses

        Args:
          addresses: An array of address objects, each specifying a property location.

          filters: An _optional_ object containing criteria to refine the rental comps search, such
              as date range, price, number of bedrooms, etc. If no filters are provided, the
              search will include all available comps.

          num_comps: An _optional_ int containing the number of rental comps to return per subject
              address. The minimum value is 1 and the maximum value is 50. If no value is
              provided, we will return our top 10 comps.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/data/rental-comps",
            body=maybe_transform(
                {
                    "addresses": addresses,
                    "filters": filters,
                    "num_comps": num_comps,
                },
                rental_comps_fetch_params.RentalCompsFetchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RentalCompsResponse,
        )


class AsyncRentalCompsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRentalCompsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRentalCompsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRentalCompsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#with_streaming_response
        """
        return AsyncRentalCompsResourceWithStreamingResponse(self)

    async def _fetch(
        self,
        *,
        addresses: Iterable[rental_comps_fetch_params.Address],
        filters: Optional[rental_comps_fetch_params.Filters] | NotGiven = NOT_GIVEN,
        num_comps: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RentalCompsResponse:
        """
        Fetch rental comps for addresses

        Args:
          addresses: An array of address objects, each specifying a property location.

          filters: An _optional_ object containing criteria to refine the rental comps search, such
              as date range, price, number of bedrooms, etc. If no filters are provided, the
              search will include all available comps.

          num_comps: An _optional_ int containing the number of rental comps to return per subject
              address. The minimum value is 1 and the maximum value is 50. If no value is
              provided, we will return our top 10 comps.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/data/rental-comps",
            body=await async_maybe_transform(
                {
                    "addresses": addresses,
                    "filters": filters,
                    "num_comps": num_comps,
                },
                rental_comps_fetch_params.RentalCompsFetchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RentalCompsResponse,
        )


class RentalCompsResourceWithRawResponse:
    def __init__(self, rental_comps: RentalCompsResource) -> None:
        self._rental_comps = rental_comps

        self._fetch = to_raw_response_wrapper(
            rental_comps._fetch,
        )


class AsyncRentalCompsResourceWithRawResponse:
    def __init__(self, rental_comps: AsyncRentalCompsResource) -> None:
        self._rental_comps = rental_comps

        self._fetch = async_to_raw_response_wrapper(
            rental_comps._fetch,
        )


class RentalCompsResourceWithStreamingResponse:
    def __init__(self, rental_comps: RentalCompsResource) -> None:
        self._rental_comps = rental_comps

        self._fetch = to_streamed_response_wrapper(
            rental_comps._fetch,
        )


class AsyncRentalCompsResourceWithStreamingResponse:
    def __init__(self, rental_comps: AsyncRentalCompsResource) -> None:
        self._rental_comps = rental_comps

        self._fetch = async_to_streamed_response_wrapper(
            rental_comps._fetch,
        )
