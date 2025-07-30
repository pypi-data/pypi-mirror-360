# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import collections
import concurrent.futures.thread
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
from ...types.data import property_details_response, property_details_fetch_params
from ..._base_client import make_request_options
from ...types.data.property_details_response import PropertyDetailsResponse

if TYPE_CHECKING:
    from ... import Mainstay

__all__ = ["PropertyDetailsResource", "AsyncPropertyDetailsResource"]


MAX_CONCURRENT_REQUESTS = 4
MAX_ADDRESSES_PER_PROPERTY_DETAILS_REQUEST = 50


class PropertyDetailsResource(SyncAPIResource):
    def __init__(self, client: Mainstay) -> None:
        super().__init__(client)
        self._executor = concurrent.futures.thread.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS)

    @cached_property
    def with_raw_response(self) -> PropertyDetailsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#accessing-raw-response-data-eg-headers
        """
        return PropertyDetailsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PropertyDetailsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#with_streaming_response
        """
        return PropertyDetailsResourceWithStreamingResponse(self)

    # noinspection DuplicatedCode
    def fetch(
        self,
        *,
        addresses: Iterable[property_details_fetch_params.Address],
        max_addresses_per_request: int = MAX_ADDRESSES_PER_PROPERTY_DETAILS_REQUEST,
        #
        # Stainless arguments.
        #
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Iterable[property_details_response.Result]:
        """
        Fetch property details for addresses (custom code)

        Args:
          addresses: An array of address objects, each specifying a property location.

          max_addresses_per_request: The maximum number of addresses to include in each request.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        futures: Deque[concurrent.futures.Future[PropertyDetailsResponse]] = collections.deque()
        address_iter = iter(addresses)

        def submit_request() -> None:
            chunked_addresses: list[property_details_fetch_params.Address] = []
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
            response = future.result()  # Block until the future is done
            submit_request()

            yield from response.results

    def _fetch(
        self,
        *,
        addresses: Iterable[property_details_fetch_params.Address],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PropertyDetailsResponse:
        """
        Fetch property details for addresses

        Args:
          addresses: An array of address objects, each specifying a property location.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/data/property-details",
            body=maybe_transform({"addresses": addresses}, property_details_fetch_params.PropertyDetailsFetchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PropertyDetailsResponse,
        )


class AsyncPropertyDetailsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPropertyDetailsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPropertyDetailsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPropertyDetailsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/mainstay-io/mainstay-python#with_streaming_response
        """
        return AsyncPropertyDetailsResourceWithStreamingResponse(self)

    async def _fetch(
        self,
        *,
        addresses: Iterable[property_details_fetch_params.Address],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PropertyDetailsResponse:
        """
        Fetch property details for addresses

        Args:
          addresses: An array of address objects, each specifying a property location.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/data/property-details",
            body=await async_maybe_transform(
                {"addresses": addresses}, property_details_fetch_params.PropertyDetailsFetchParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PropertyDetailsResponse,
        )


class PropertyDetailsResourceWithRawResponse:
    def __init__(self, property_details: PropertyDetailsResource) -> None:
        self._property_details = property_details

        self._fetch = to_raw_response_wrapper(
            property_details._fetch,
        )


class AsyncPropertyDetailsResourceWithRawResponse:
    def __init__(self, property_details: AsyncPropertyDetailsResource) -> None:
        self._property_details = property_details

        self._fetch = async_to_raw_response_wrapper(
            property_details._fetch,
        )


class PropertyDetailsResourceWithStreamingResponse:
    def __init__(self, property_details: PropertyDetailsResource) -> None:
        self._property_details = property_details

        self._fetch = to_streamed_response_wrapper(
            property_details._fetch,
        )


class AsyncPropertyDetailsResourceWithStreamingResponse:
    def __init__(self, property_details: AsyncPropertyDetailsResource) -> None:
        self._property_details = property_details

        self._fetch = async_to_streamed_response_wrapper(
            property_details._fetch,
        )
