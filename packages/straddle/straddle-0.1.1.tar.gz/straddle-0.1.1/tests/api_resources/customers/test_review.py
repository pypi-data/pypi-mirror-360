# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.types import CustomerV1
from straddle.types.customers import CustomerReviewV1

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestReview:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_decision(self, client: Straddle) -> None:
        review = client.customers.review.decision(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            status="verified",
        )
        assert_matches_type(CustomerV1, review, path=["response"])

    @parametrize
    def test_method_decision_with_all_params(self, client: Straddle) -> None:
        review = client.customers.review.decision(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            status="verified",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, review, path=["response"])

    @parametrize
    def test_raw_response_decision(self, client: Straddle) -> None:
        response = client.customers.review.with_raw_response.decision(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            status="verified",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        review = response.parse()
        assert_matches_type(CustomerV1, review, path=["response"])

    @parametrize
    def test_streaming_response_decision(self, client: Straddle) -> None:
        with client.customers.review.with_streaming_response.decision(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            status="verified",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            review = response.parse()
            assert_matches_type(CustomerV1, review, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_decision(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.customers.review.with_raw_response.decision(
                id="",
                status="verified",
            )

    @parametrize
    def test_method_get(self, client: Straddle) -> None:
        review = client.customers.review.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerReviewV1, review, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Straddle) -> None:
        review = client.customers.review.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerReviewV1, review, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Straddle) -> None:
        response = client.customers.review.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        review = response.parse()
        assert_matches_type(CustomerReviewV1, review, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Straddle) -> None:
        with client.customers.review.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            review = response.parse()
            assert_matches_type(CustomerReviewV1, review, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.customers.review.with_raw_response.get(
                id="",
            )


class TestAsyncReview:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_decision(self, async_client: AsyncStraddle) -> None:
        review = await async_client.customers.review.decision(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            status="verified",
        )
        assert_matches_type(CustomerV1, review, path=["response"])

    @parametrize
    async def test_method_decision_with_all_params(self, async_client: AsyncStraddle) -> None:
        review = await async_client.customers.review.decision(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            status="verified",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, review, path=["response"])

    @parametrize
    async def test_raw_response_decision(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.review.with_raw_response.decision(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            status="verified",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        review = await response.parse()
        assert_matches_type(CustomerV1, review, path=["response"])

    @parametrize
    async def test_streaming_response_decision(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.review.with_streaming_response.decision(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            status="verified",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            review = await response.parse()
            assert_matches_type(CustomerV1, review, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_decision(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.customers.review.with_raw_response.decision(
                id="",
                status="verified",
            )

    @parametrize
    async def test_method_get(self, async_client: AsyncStraddle) -> None:
        review = await async_client.customers.review.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerReviewV1, review, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncStraddle) -> None:
        review = await async_client.customers.review.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerReviewV1, review, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.review.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        review = await response.parse()
        assert_matches_type(CustomerReviewV1, review, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.review.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            review = await response.parse()
            assert_matches_type(CustomerReviewV1, review, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.customers.review.with_raw_response.get(
                id="",
            )
