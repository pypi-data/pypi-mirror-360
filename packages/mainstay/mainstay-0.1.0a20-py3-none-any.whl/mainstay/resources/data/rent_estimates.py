# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import collections
import concurrent.futures
from typing import TYPE_CHECKING, Deque, Iterable

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
from ...types.data import rent_estimates_response, rent_estimates_fetch_params
from ..._base_client import make_request_options
from ...types.data.rent_estimates_response import RentEstimatesResponse

if TYPE_CHECKING:
    from ... import Mainstay

__all__ = ["RentEstimatesResource", "AsyncRentEstimatesResource"]


MAX_CONCURRENT_REQUESTS = 4
MAX_ADDRESSES_PER_RENT_ESTIMATES_REQUEST = 50
class RentEstimatesResource(SyncAPIResource):
    def __init__(self, client: Mainstay) -> None:
        super().__init__(client)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS)

    @cached_property
    def with_raw_response(self) -> RentEstimatesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#accessing-raw-response-data-eg-headers
        """
        return RentEstimatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RentEstimatesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#with_streaming_response
        """
        return RentEstimatesResourceWithStreamingResponse(self)

    # noinspection DuplicatedCode
    def fetch(
        self,
        *,
        addresses: Iterable[rent_estimates_fetch_params.Address],
        max_addresses_per_request: int = MAX_ADDRESSES_PER_RENT_ESTIMATES_REQUEST,
        #
        # Stainless arguments.
        #
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Iterable[rent_estimates_response.Result]:
        """
        Fetch rent estimates for addresses (custom code)

        Args:
          addresses: An array of address objects, each specifying a property location.

          max_addresses_per_request: The maximum number of addresses to include in each request.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        futures: Deque[concurrent.futures.Future[RentEstimatesResponse]] = collections.deque()
        address_iter = iter(addresses)

        def submit_request() -> None:
            chunked_addresses: list[rent_estimates_fetch_params.Address] = []
            for address in address_iter:
                chunked_addresses.append(address)
                if len(chunked_addresses) >= max_addresses_per_request:
                    break
            if chunked_addresses:
                futures.append(
                    self._executor.submit(
                        self._fetch,
                        addresses=chunked_addresses,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        extra_body=extra_body,
                        timeout=timeout,
                    )
                )

        # Submit initial requests. MAX_CONCURRENT_REQUESTS will be submitted and also queue up.
        for _ in range(MAX_CONCURRENT_REQUESTS * 2):
            submit_request()

        while futures:
            future = futures.popleft()
            response = future.result()
            submit_request()

            yield from response.results

    def _fetch(
        self,
        *,
        addresses: Iterable[rent_estimates_fetch_params.Address],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RentEstimatesResponse:
        """
        Fetch rent estimates for addresses

        Args:
          addresses: An array of address objects, each specifying a property location.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/data/rent-estimates",
            body=maybe_transform({"addresses": addresses}, rent_estimates_fetch_params.RentEstimatesFetchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RentEstimatesResponse,
        )


class AsyncRentEstimatesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRentEstimatesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRentEstimatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRentEstimatesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#with_streaming_response
        """
        return AsyncRentEstimatesResourceWithStreamingResponse(self)

    async def _fetch(
        self,
        *,
        addresses: Iterable[rent_estimates_fetch_params.Address],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RentEstimatesResponse:
        """
        Fetch rent estimates for addresses

        Args:
          addresses: An array of address objects, each specifying a property location.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/data/rent-estimates",
            body=await async_maybe_transform(
                {"addresses": addresses}, rent_estimates_fetch_params.RentEstimatesFetchParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RentEstimatesResponse,
        )


class RentEstimatesResourceWithRawResponse:
    def __init__(self, rent_estimates: RentEstimatesResource) -> None:
        self._rent_estimates = rent_estimates

        self._fetch = to_raw_response_wrapper(
            rent_estimates._fetch,
        )


class AsyncRentEstimatesResourceWithRawResponse:
    def __init__(self, rent_estimates: AsyncRentEstimatesResource) -> None:
        self._rent_estimates = rent_estimates

        self._fetch = async_to_raw_response_wrapper(
            rent_estimates._fetch,
        )


class RentEstimatesResourceWithStreamingResponse:
    def __init__(self, rent_estimates: RentEstimatesResource) -> None:
        self._rent_estimates = rent_estimates

        self._fetch = to_streamed_response_wrapper(
            rent_estimates._fetch,
        )


class AsyncRentEstimatesResourceWithStreamingResponse:
    def __init__(self, rent_estimates: AsyncRentEstimatesResource) -> None:
        self._rent_estimates = rent_estimates

        self._fetch = async_to_streamed_response_wrapper(
            rent_estimates._fetch,
        )
