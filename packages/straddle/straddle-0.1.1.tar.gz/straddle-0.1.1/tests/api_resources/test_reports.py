# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.types import ReportCreateTotalCustomersByStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestReports:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_total_customers_by_status(self, client: Straddle) -> None:
        report = client.reports.create_total_customers_by_status()
        assert_matches_type(ReportCreateTotalCustomersByStatusResponse, report, path=["response"])

    @parametrize
    def test_method_create_total_customers_by_status_with_all_params(self, client: Straddle) -> None:
        report = client.reports.create_total_customers_by_status(
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ReportCreateTotalCustomersByStatusResponse, report, path=["response"])

    @parametrize
    def test_raw_response_create_total_customers_by_status(self, client: Straddle) -> None:
        response = client.reports.with_raw_response.create_total_customers_by_status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        report = response.parse()
        assert_matches_type(ReportCreateTotalCustomersByStatusResponse, report, path=["response"])

    @parametrize
    def test_streaming_response_create_total_customers_by_status(self, client: Straddle) -> None:
        with client.reports.with_streaming_response.create_total_customers_by_status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            report = response.parse()
            assert_matches_type(ReportCreateTotalCustomersByStatusResponse, report, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncReports:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_total_customers_by_status(self, async_client: AsyncStraddle) -> None:
        report = await async_client.reports.create_total_customers_by_status()
        assert_matches_type(ReportCreateTotalCustomersByStatusResponse, report, path=["response"])

    @parametrize
    async def test_method_create_total_customers_by_status_with_all_params(self, async_client: AsyncStraddle) -> None:
        report = await async_client.reports.create_total_customers_by_status(
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ReportCreateTotalCustomersByStatusResponse, report, path=["response"])

    @parametrize
    async def test_raw_response_create_total_customers_by_status(self, async_client: AsyncStraddle) -> None:
        response = await async_client.reports.with_raw_response.create_total_customers_by_status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        report = await response.parse()
        assert_matches_type(ReportCreateTotalCustomersByStatusResponse, report, path=["response"])

    @parametrize
    async def test_streaming_response_create_total_customers_by_status(self, async_client: AsyncStraddle) -> None:
        async with async_client.reports.with_streaming_response.create_total_customers_by_status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            report = await response.parse()
            assert_matches_type(ReportCreateTotalCustomersByStatusResponse, report, path=["response"])

        assert cast(Any, response.is_closed) is True
