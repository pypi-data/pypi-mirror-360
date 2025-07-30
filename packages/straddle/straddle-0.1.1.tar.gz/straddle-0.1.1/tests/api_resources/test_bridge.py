# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.types import BridgeTokenV1

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBridge:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_initialize(self, client: Straddle) -> None:
        bridge = client.bridge.initialize(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(BridgeTokenV1, bridge, path=["response"])

    @parametrize
    def test_method_initialize_with_all_params(self, client: Straddle) -> None:
        bridge = client.bridge.initialize(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            config={"sandbox_outcome": "standard"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(BridgeTokenV1, bridge, path=["response"])

    @parametrize
    def test_raw_response_initialize(self, client: Straddle) -> None:
        response = client.bridge.with_raw_response.initialize(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bridge = response.parse()
        assert_matches_type(BridgeTokenV1, bridge, path=["response"])

    @parametrize
    def test_streaming_response_initialize(self, client: Straddle) -> None:
        with client.bridge.with_streaming_response.initialize(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bridge = response.parse()
            assert_matches_type(BridgeTokenV1, bridge, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBridge:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_initialize(self, async_client: AsyncStraddle) -> None:
        bridge = await async_client.bridge.initialize(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(BridgeTokenV1, bridge, path=["response"])

    @parametrize
    async def test_method_initialize_with_all_params(self, async_client: AsyncStraddle) -> None:
        bridge = await async_client.bridge.initialize(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            config={"sandbox_outcome": "standard"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(BridgeTokenV1, bridge, path=["response"])

    @parametrize
    async def test_raw_response_initialize(self, async_client: AsyncStraddle) -> None:
        response = await async_client.bridge.with_raw_response.initialize(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bridge = await response.parse()
        assert_matches_type(BridgeTokenV1, bridge, path=["response"])

    @parametrize
    async def test_streaming_response_initialize(self, async_client: AsyncStraddle) -> None:
        async with async_client.bridge.with_streaming_response.initialize(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bridge = await response.parse()
            assert_matches_type(BridgeTokenV1, bridge, path=["response"])

        assert cast(Any, response.is_closed) is True
