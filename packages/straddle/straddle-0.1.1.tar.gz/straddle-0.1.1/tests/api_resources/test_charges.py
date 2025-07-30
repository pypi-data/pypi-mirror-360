# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.types import (
    ChargeV1,
    ChargeUnmaskResponse,
)
from straddle._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCharges:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Straddle) -> None:
        charge = client.charges.create(
            amount=10000,
            config={"balance_check": "required"},
            consent_type="internet",
            currency="currency",
            description="Monthly subscription fee",
            device={"ip_address": "192.168.1.1"},
            external_id="external_id",
            paykey="paykey",
            payment_date=parse_date("2019-12-27"),
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Straddle) -> None:
        charge = client.charges.create(
            amount=10000,
            config={
                "balance_check": "required",
                "sandbox_outcome": "standard",
            },
            consent_type="internet",
            currency="currency",
            description="Monthly subscription fee",
            device={"ip_address": "192.168.1.1"},
            external_id="external_id",
            paykey="paykey",
            payment_date=parse_date("2019-12-27"),
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Straddle) -> None:
        response = client.charges.with_raw_response.create(
            amount=10000,
            config={"balance_check": "required"},
            consent_type="internet",
            currency="currency",
            description="Monthly subscription fee",
            device={"ip_address": "192.168.1.1"},
            external_id="external_id",
            paykey="paykey",
            payment_date=parse_date("2019-12-27"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Straddle) -> None:
        with client.charges.with_streaming_response.create(
            amount=10000,
            config={"balance_check": "required"},
            consent_type="internet",
            currency="currency",
            description="Monthly subscription fee",
            device={"ip_address": "192.168.1.1"},
            external_id="external_id",
            paykey="paykey",
            payment_date=parse_date("2019-12-27"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Straddle) -> None:
        charge = client.charges.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            amount=10000,
            description="Monthly subscription fee",
            payment_date=parse_date("2019-12-27"),
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Straddle) -> None:
        charge = client.charges.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            amount=10000,
            description="Monthly subscription fee",
            payment_date=parse_date("2019-12-27"),
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Straddle) -> None:
        response = client.charges.with_raw_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            amount=10000,
            description="Monthly subscription fee",
            payment_date=parse_date("2019-12-27"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Straddle) -> None:
        with client.charges.with_streaming_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            amount=10000,
            description="Monthly subscription fee",
            payment_date=parse_date("2019-12-27"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.charges.with_raw_response.update(
                id="",
                amount=10000,
                description="Monthly subscription fee",
                payment_date=parse_date("2019-12-27"),
            )

    @parametrize
    def test_method_cancel(self, client: Straddle) -> None:
        charge = client.charges.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_method_cancel_with_all_params(self, client: Straddle) -> None:
        charge = client.charges.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reason="reason",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Straddle) -> None:
        response = client.charges.with_raw_response.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Straddle) -> None:
        with client.charges.with_streaming_response.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.charges.with_raw_response.cancel(
                id="",
            )

    @parametrize
    def test_method_get(self, client: Straddle) -> None:
        charge = client.charges.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Straddle) -> None:
        charge = client.charges.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Straddle) -> None:
        response = client.charges.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Straddle) -> None:
        with client.charges.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.charges.with_raw_response.get(
                id="",
            )

    @parametrize
    def test_method_hold(self, client: Straddle) -> None:
        charge = client.charges.hold(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_method_hold_with_all_params(self, client: Straddle) -> None:
        charge = client.charges.hold(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reason="reason",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_raw_response_hold(self, client: Straddle) -> None:
        response = client.charges.with_raw_response.hold(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_streaming_response_hold(self, client: Straddle) -> None:
        with client.charges.with_streaming_response.hold(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_hold(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.charges.with_raw_response.hold(
                id="",
            )

    @parametrize
    def test_method_release(self, client: Straddle) -> None:
        charge = client.charges.release(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_method_release_with_all_params(self, client: Straddle) -> None:
        charge = client.charges.release(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reason="reason",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_raw_response_release(self, client: Straddle) -> None:
        response = client.charges.with_raw_response.release(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    def test_streaming_response_release(self, client: Straddle) -> None:
        with client.charges.with_streaming_response.release(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_release(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.charges.with_raw_response.release(
                id="",
            )

    @parametrize
    def test_method_unmask(self, client: Straddle) -> None:
        charge = client.charges.unmask(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeUnmaskResponse, charge, path=["response"])

    @parametrize
    def test_method_unmask_with_all_params(self, client: Straddle) -> None:
        charge = client.charges.unmask(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeUnmaskResponse, charge, path=["response"])

    @parametrize
    def test_raw_response_unmask(self, client: Straddle) -> None:
        response = client.charges.with_raw_response.unmask(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = response.parse()
        assert_matches_type(ChargeUnmaskResponse, charge, path=["response"])

    @parametrize
    def test_streaming_response_unmask(self, client: Straddle) -> None:
        with client.charges.with_streaming_response.unmask(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = response.parse()
            assert_matches_type(ChargeUnmaskResponse, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_unmask(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.charges.with_raw_response.unmask(
                id="",
            )


class TestAsyncCharges:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.create(
            amount=10000,
            config={"balance_check": "required"},
            consent_type="internet",
            currency="currency",
            description="Monthly subscription fee",
            device={"ip_address": "192.168.1.1"},
            external_id="external_id",
            paykey="paykey",
            payment_date=parse_date("2019-12-27"),
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.create(
            amount=10000,
            config={
                "balance_check": "required",
                "sandbox_outcome": "standard",
            },
            consent_type="internet",
            currency="currency",
            description="Monthly subscription fee",
            device={"ip_address": "192.168.1.1"},
            external_id="external_id",
            paykey="paykey",
            payment_date=parse_date("2019-12-27"),
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStraddle) -> None:
        response = await async_client.charges.with_raw_response.create(
            amount=10000,
            config={"balance_check": "required"},
            consent_type="internet",
            currency="currency",
            description="Monthly subscription fee",
            device={"ip_address": "192.168.1.1"},
            external_id="external_id",
            paykey="paykey",
            payment_date=parse_date("2019-12-27"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = await response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStraddle) -> None:
        async with async_client.charges.with_streaming_response.create(
            amount=10000,
            config={"balance_check": "required"},
            consent_type="internet",
            currency="currency",
            description="Monthly subscription fee",
            device={"ip_address": "192.168.1.1"},
            external_id="external_id",
            paykey="paykey",
            payment_date=parse_date("2019-12-27"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = await response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            amount=10000,
            description="Monthly subscription fee",
            payment_date=parse_date("2019-12-27"),
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            amount=10000,
            description="Monthly subscription fee",
            payment_date=parse_date("2019-12-27"),
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncStraddle) -> None:
        response = await async_client.charges.with_raw_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            amount=10000,
            description="Monthly subscription fee",
            payment_date=parse_date("2019-12-27"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = await response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncStraddle) -> None:
        async with async_client.charges.with_streaming_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            amount=10000,
            description="Monthly subscription fee",
            payment_date=parse_date("2019-12-27"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = await response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.charges.with_raw_response.update(
                id="",
                amount=10000,
                description="Monthly subscription fee",
                payment_date=parse_date("2019-12-27"),
            )

    @parametrize
    async def test_method_cancel(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_method_cancel_with_all_params(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reason="reason",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncStraddle) -> None:
        response = await async_client.charges.with_raw_response.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = await response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncStraddle) -> None:
        async with async_client.charges.with_streaming_response.cancel(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = await response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.charges.with_raw_response.cancel(
                id="",
            )

    @parametrize
    async def test_method_get(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncStraddle) -> None:
        response = await async_client.charges.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = await response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncStraddle) -> None:
        async with async_client.charges.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = await response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.charges.with_raw_response.get(
                id="",
            )

    @parametrize
    async def test_method_hold(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.hold(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_method_hold_with_all_params(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.hold(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reason="reason",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_raw_response_hold(self, async_client: AsyncStraddle) -> None:
        response = await async_client.charges.with_raw_response.hold(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = await response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_streaming_response_hold(self, async_client: AsyncStraddle) -> None:
        async with async_client.charges.with_streaming_response.hold(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = await response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_hold(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.charges.with_raw_response.hold(
                id="",
            )

    @parametrize
    async def test_method_release(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.release(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_method_release_with_all_params(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.release(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reason="reason",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_raw_response_release(self, async_client: AsyncStraddle) -> None:
        response = await async_client.charges.with_raw_response.release(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = await response.parse()
        assert_matches_type(ChargeV1, charge, path=["response"])

    @parametrize
    async def test_streaming_response_release(self, async_client: AsyncStraddle) -> None:
        async with async_client.charges.with_streaming_response.release(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = await response.parse()
            assert_matches_type(ChargeV1, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_release(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.charges.with_raw_response.release(
                id="",
            )

    @parametrize
    async def test_method_unmask(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.unmask(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeUnmaskResponse, charge, path=["response"])

    @parametrize
    async def test_method_unmask_with_all_params(self, async_client: AsyncStraddle) -> None:
        charge = await async_client.charges.unmask(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ChargeUnmaskResponse, charge, path=["response"])

    @parametrize
    async def test_raw_response_unmask(self, async_client: AsyncStraddle) -> None:
        response = await async_client.charges.with_raw_response.unmask(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        charge = await response.parse()
        assert_matches_type(ChargeUnmaskResponse, charge, path=["response"])

    @parametrize
    async def test_streaming_response_unmask(self, async_client: AsyncStraddle) -> None:
        async with async_client.charges.with_streaming_response.unmask(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            charge = await response.parse()
            assert_matches_type(ChargeUnmaskResponse, charge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_unmask(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.charges.with_raw_response.unmask(
                id="",
            )
