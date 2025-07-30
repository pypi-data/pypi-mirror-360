# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.types import FundingEventSummaryItemV1
from straddle._utils import parse_date
from straddle.pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from straddle.types.funding_event_summary_paged_v1 import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFundingEvents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Straddle) -> None:
        funding_event = client.funding_events.list()
        assert_matches_type(SyncPageNumberSchema[Data], funding_event, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Straddle) -> None:
        funding_event = client.funding_events.list(
            created_from=parse_date("2019-12-27"),
            created_to=parse_date("2019-12-27"),
            direction="deposit",
            event_type="charge_deposit",
            page_number=0,
            page_size=0,
            sort_by="transfer_date",
            sort_order="asc",
            trace_number="trace_number",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncPageNumberSchema[Data], funding_event, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Straddle) -> None:
        response = client.funding_events.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        funding_event = response.parse()
        assert_matches_type(SyncPageNumberSchema[Data], funding_event, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Straddle) -> None:
        with client.funding_events.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            funding_event = response.parse()
            assert_matches_type(SyncPageNumberSchema[Data], funding_event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Straddle) -> None:
        funding_event = client.funding_events.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(FundingEventSummaryItemV1, funding_event, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Straddle) -> None:
        funding_event = client.funding_events.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(FundingEventSummaryItemV1, funding_event, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Straddle) -> None:
        response = client.funding_events.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        funding_event = response.parse()
        assert_matches_type(FundingEventSummaryItemV1, funding_event, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Straddle) -> None:
        with client.funding_events.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            funding_event = response.parse()
            assert_matches_type(FundingEventSummaryItemV1, funding_event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.funding_events.with_raw_response.get(
                id="",
            )


class TestAsyncFundingEvents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncStraddle) -> None:
        funding_event = await async_client.funding_events.list()
        assert_matches_type(AsyncPageNumberSchema[Data], funding_event, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStraddle) -> None:
        funding_event = await async_client.funding_events.list(
            created_from=parse_date("2019-12-27"),
            created_to=parse_date("2019-12-27"),
            direction="deposit",
            event_type="charge_deposit",
            page_number=0,
            page_size=0,
            sort_by="transfer_date",
            sort_order="asc",
            trace_number="trace_number",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], funding_event, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStraddle) -> None:
        response = await async_client.funding_events.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        funding_event = await response.parse()
        assert_matches_type(AsyncPageNumberSchema[Data], funding_event, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStraddle) -> None:
        async with async_client.funding_events.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            funding_event = await response.parse()
            assert_matches_type(AsyncPageNumberSchema[Data], funding_event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncStraddle) -> None:
        funding_event = await async_client.funding_events.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(FundingEventSummaryItemV1, funding_event, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncStraddle) -> None:
        funding_event = await async_client.funding_events.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(FundingEventSummaryItemV1, funding_event, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncStraddle) -> None:
        response = await async_client.funding_events.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        funding_event = await response.parse()
        assert_matches_type(FundingEventSummaryItemV1, funding_event, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncStraddle) -> None:
        async with async_client.funding_events.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            funding_event = await response.parse()
            assert_matches_type(FundingEventSummaryItemV1, funding_event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.funding_events.with_raw_response.get(
                id="",
            )
