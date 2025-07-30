# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle._utils import parse_date, parse_datetime
from straddle.pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from straddle.types.payment_summary_paged_v1 import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPayments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Straddle) -> None:
        payment = client.payments.list()
        assert_matches_type(SyncPageNumberSchema[Data], payment, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Straddle) -> None:
        payment = client.payments.list(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            default_page_size=0,
            default_sort="created_at",
            default_sort_order="asc",
            external_id="external_id",
            funding_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            max_amount=0,
            max_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            max_effective_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            max_payment_date=parse_date("2019-12-27"),
            min_amount=0,
            min_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            min_effective_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            min_payment_date=parse_date("2019-12-27"),
            page_number=0,
            page_size=0,
            paykey="paykey",
            paykey_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            payment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            payment_status=["created"],
            payment_type=["charge"],
            search_text="search_text",
            sort_by="created_at",
            sort_order="asc",
            status_reason=["insufficient_funds"],
            status_source=["watchtower"],
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncPageNumberSchema[Data], payment, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Straddle) -> None:
        response = client.payments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        payment = response.parse()
        assert_matches_type(SyncPageNumberSchema[Data], payment, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Straddle) -> None:
        with client.payments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            payment = response.parse()
            assert_matches_type(SyncPageNumberSchema[Data], payment, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPayments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncStraddle) -> None:
        payment = await async_client.payments.list()
        assert_matches_type(AsyncPageNumberSchema[Data], payment, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStraddle) -> None:
        payment = await async_client.payments.list(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            default_page_size=0,
            default_sort="created_at",
            default_sort_order="asc",
            external_id="external_id",
            funding_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            max_amount=0,
            max_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            max_effective_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            max_payment_date=parse_date("2019-12-27"),
            min_amount=0,
            min_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            min_effective_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            min_payment_date=parse_date("2019-12-27"),
            page_number=0,
            page_size=0,
            paykey="paykey",
            paykey_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            payment_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            payment_status=["created"],
            payment_type=["charge"],
            search_text="search_text",
            sort_by="created_at",
            sort_order="asc",
            status_reason=["insufficient_funds"],
            status_source=["watchtower"],
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], payment, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStraddle) -> None:
        response = await async_client.payments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        payment = await response.parse()
        assert_matches_type(AsyncPageNumberSchema[Data], payment, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStraddle) -> None:
        async with async_client.payments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            payment = await response.parse()
            assert_matches_type(AsyncPageNumberSchema[Data], payment, path=["response"])

        assert cast(Any, response.is_closed) is True
