# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from mainstay import Mainstay, AsyncMainstay
from tests.utils import assert_matches_type
from mainstay.types.data import SchoolRatingsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSchoolRatings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_fetch(self, client: Mainstay) -> None:
        school_ratings = client.data.school_ratings._fetch(
            addresses=[
                {
                    "city": "San Antonio",
                    "postal_code": "78253",
                    "state": "TX",
                    "street": "14042 Kenyte Row",
                }
            ],
        )
        assert_matches_type(SchoolRatingsResponse, school_ratings, path=["response"])

    @parametrize
    def test_raw_response_fetch(self, client: Mainstay) -> None:
        response = client.data.school_ratings.with_raw_response._fetch(
            addresses=[
                {
                    "city": "San Antonio",
                    "postal_code": "78253",
                    "state": "TX",
                    "street": "14042 Kenyte Row",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        school_ratings = response.parse()
        assert_matches_type(SchoolRatingsResponse, school_ratings, path=["response"])

    @parametrize
    def test_streaming_response_fetch(self, client: Mainstay) -> None:
        with client.data.school_ratings.with_streaming_response._fetch(
            addresses=[
                {
                    "city": "San Antonio",
                    "postal_code": "78253",
                    "state": "TX",
                    "street": "14042 Kenyte Row",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            school_ratings = response.parse()
            assert_matches_type(SchoolRatingsResponse, school_ratings, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSchoolRatings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_fetch(self, async_client: AsyncMainstay) -> None:
        school_ratings = await async_client.data.school_ratings._fetch(
            addresses=[
                {
                    "city": "San Antonio",
                    "postal_code": "78253",
                    "state": "TX",
                    "street": "14042 Kenyte Row",
                }
            ],
        )
        assert_matches_type(SchoolRatingsResponse, school_ratings, path=["response"])

    @parametrize
    async def test_raw_response_fetch(self, async_client: AsyncMainstay) -> None:
        response = await async_client.data.school_ratings.with_raw_response._fetch(
            addresses=[
                {
                    "city": "San Antonio",
                    "postal_code": "78253",
                    "state": "TX",
                    "street": "14042 Kenyte Row",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        school_ratings = await response.parse()
        assert_matches_type(SchoolRatingsResponse, school_ratings, path=["response"])

    @parametrize
    async def test_streaming_response_fetch(self, async_client: AsyncMainstay) -> None:
        async with async_client.data.school_ratings.with_streaming_response._fetch(
            addresses=[
                {
                    "city": "San Antonio",
                    "postal_code": "78253",
                    "state": "TX",
                    "street": "14042 Kenyte Row",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            school_ratings = await response.parse()
            assert_matches_type(SchoolRatingsResponse, school_ratings, path=["response"])

        assert cast(Any, response.is_closed) is True
