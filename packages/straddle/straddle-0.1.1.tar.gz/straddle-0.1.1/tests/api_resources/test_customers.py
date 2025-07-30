# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.types import (
    CustomerV1,
    CustomerUnmaskedV1,
)
from straddle._utils import parse_date, parse_datetime
from straddle.pagination import SyncPageNumberSchema, AsyncPageNumberSchema
from straddle.types.customer_summary_paged_v1 import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCustomers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Straddle) -> None:
        customer = client.customers.create(
            device={"ip_address": "192.168.1.1"},
            email="ron.swanson@pawnee.com",
            name="Ron Swanson",
            phone="+12128675309",
            type="individual",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Straddle) -> None:
        customer = client.customers.create(
            device={"ip_address": "192.168.1.1"},
            email="ron.swanson@pawnee.com",
            name="Ron Swanson",
            phone="+12128675309",
            type="individual",
            address={
                "address1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "address2": "Apt 1",
            },
            compliance_profile={
                "dob": parse_date("1969-04-20"),
                "ssn": "123-45-6789",
            },
            config={
                "processing_method": "inline",
                "sandbox_outcome": "standard",
            },
            external_id="customer_123",
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Straddle) -> None:
        response = client.customers.with_raw_response.create(
            device={"ip_address": "192.168.1.1"},
            email="ron.swanson@pawnee.com",
            name="Ron Swanson",
            phone="+12128675309",
            type="individual",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Straddle) -> None:
        with client.customers.with_streaming_response.create(
            device={"ip_address": "192.168.1.1"},
            email="ron.swanson@pawnee.com",
            name="Ron Swanson",
            phone="+12128675309",
            type="individual",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Straddle) -> None:
        customer = client.customers.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            device={"ip_address": "192.168.1.1"},
            email="dev@stainless.com",
            name="name",
            phone="+46991022",
            status="pending",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Straddle) -> None:
        customer = client.customers.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            device={"ip_address": "192.168.1.1"},
            email="dev@stainless.com",
            name="name",
            phone="+46991022",
            status="pending",
            address={
                "address1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "address2": "Apt 1",
            },
            compliance_profile={
                "dob": parse_date("1969-04-20"),
                "ssn": "123-45-6789",
            },
            external_id="external_id",
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Straddle) -> None:
        response = client.customers.with_raw_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            device={"ip_address": "192.168.1.1"},
            email="dev@stainless.com",
            name="name",
            phone="+46991022",
            status="pending",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Straddle) -> None:
        with client.customers.with_streaming_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            device={"ip_address": "192.168.1.1"},
            email="dev@stainless.com",
            name="name",
            phone="+46991022",
            status="pending",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.customers.with_raw_response.update(
                id="",
                device={"ip_address": "192.168.1.1"},
                email="dev@stainless.com",
                name="name",
                phone="+46991022",
                status="pending",
            )

    @parametrize
    def test_method_list(self, client: Straddle) -> None:
        customer = client.customers.list()
        assert_matches_type(SyncPageNumberSchema[Data], customer, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Straddle) -> None:
        customer = client.customers.list(
            created_from=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_to=parse_datetime("2019-12-27T18:11:19.117Z"),
            email="email",
            external_id="external_id",
            name="name",
            page_number=0,
            page_size=0,
            search_text="search_text",
            sort_by="name",
            sort_order="asc",
            status=["pending"],
            types=["individual"],
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SyncPageNumberSchema[Data], customer, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Straddle) -> None:
        response = client.customers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(SyncPageNumberSchema[Data], customer, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Straddle) -> None:
        with client.customers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(SyncPageNumberSchema[Data], customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Straddle) -> None:
        customer = client.customers.delete(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_method_delete_with_all_params(self, client: Straddle) -> None:
        customer = client.customers.delete(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Straddle) -> None:
        response = client.customers.with_raw_response.delete(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Straddle) -> None:
        with client.customers.with_streaming_response.delete(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.customers.with_raw_response.delete(
                id="",
            )

    @parametrize
    def test_method_get(self, client: Straddle) -> None:
        customer = client.customers.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Straddle) -> None:
        customer = client.customers.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Straddle) -> None:
        response = client.customers.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Straddle) -> None:
        with client.customers.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.customers.with_raw_response.get(
                id="",
            )

    @parametrize
    def test_method_refresh_review(self, client: Straddle) -> None:
        customer = client.customers.refresh_review(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_method_refresh_review_with_all_params(self, client: Straddle) -> None:
        customer = client.customers.refresh_review(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_raw_response_refresh_review(self, client: Straddle) -> None:
        response = client.customers.with_raw_response.refresh_review(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    def test_streaming_response_refresh_review(self, client: Straddle) -> None:
        with client.customers.with_streaming_response.refresh_review(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_refresh_review(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.customers.with_raw_response.refresh_review(
                id="",
            )

    @parametrize
    def test_method_unmasked(self, client: Straddle) -> None:
        customer = client.customers.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerUnmaskedV1, customer, path=["response"])

    @parametrize
    def test_method_unmasked_with_all_params(self, client: Straddle) -> None:
        customer = client.customers.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerUnmaskedV1, customer, path=["response"])

    @parametrize
    def test_raw_response_unmasked(self, client: Straddle) -> None:
        response = client.customers.with_raw_response.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerUnmaskedV1, customer, path=["response"])

    @parametrize
    def test_streaming_response_unmasked(self, client: Straddle) -> None:
        with client.customers.with_streaming_response.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerUnmaskedV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_unmasked(self, client: Straddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.customers.with_raw_response.unmasked(
                id="",
            )


class TestAsyncCustomers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.create(
            device={"ip_address": "192.168.1.1"},
            email="ron.swanson@pawnee.com",
            name="Ron Swanson",
            phone="+12128675309",
            type="individual",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.create(
            device={"ip_address": "192.168.1.1"},
            email="ron.swanson@pawnee.com",
            name="Ron Swanson",
            phone="+12128675309",
            type="individual",
            address={
                "address1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "address2": "Apt 1",
            },
            compliance_profile={
                "dob": parse_date("1969-04-20"),
                "ssn": "123-45-6789",
            },
            config={
                "processing_method": "inline",
                "sandbox_outcome": "standard",
            },
            external_id="customer_123",
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.with_raw_response.create(
            device={"ip_address": "192.168.1.1"},
            email="ron.swanson@pawnee.com",
            name="Ron Swanson",
            phone="+12128675309",
            type="individual",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.with_streaming_response.create(
            device={"ip_address": "192.168.1.1"},
            email="ron.swanson@pawnee.com",
            name="Ron Swanson",
            phone="+12128675309",
            type="individual",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            device={"ip_address": "192.168.1.1"},
            email="dev@stainless.com",
            name="name",
            phone="+46991022",
            status="pending",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            device={"ip_address": "192.168.1.1"},
            email="dev@stainless.com",
            name="name",
            phone="+46991022",
            status="pending",
            address={
                "address1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "address2": "Apt 1",
            },
            compliance_profile={
                "dob": parse_date("1969-04-20"),
                "ssn": "123-45-6789",
            },
            external_id="external_id",
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.with_raw_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            device={"ip_address": "192.168.1.1"},
            email="dev@stainless.com",
            name="name",
            phone="+46991022",
            status="pending",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.with_streaming_response.update(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            device={"ip_address": "192.168.1.1"},
            email="dev@stainless.com",
            name="name",
            phone="+46991022",
            status="pending",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.customers.with_raw_response.update(
                id="",
                device={"ip_address": "192.168.1.1"},
                email="dev@stainless.com",
                name="name",
                phone="+46991022",
                status="pending",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.list()
        assert_matches_type(AsyncPageNumberSchema[Data], customer, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.list(
            created_from=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_to=parse_datetime("2019-12-27T18:11:19.117Z"),
            email="email",
            external_id="external_id",
            name="name",
            page_number=0,
            page_size=0,
            search_text="search_text",
            sort_by="name",
            sort_order="asc",
            status=["pending"],
            types=["individual"],
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AsyncPageNumberSchema[Data], customer, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(AsyncPageNumberSchema[Data], customer, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(AsyncPageNumberSchema[Data], customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.delete(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.delete(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.with_raw_response.delete(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.with_streaming_response.delete(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.customers.with_raw_response.delete(
                id="",
            )

    @parametrize
    async def test_method_get(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.with_raw_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.with_streaming_response.get(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.customers.with_raw_response.get(
                id="",
            )

    @parametrize
    async def test_method_refresh_review(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.refresh_review(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_method_refresh_review_with_all_params(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.refresh_review(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_raw_response_refresh_review(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.with_raw_response.refresh_review(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerV1, customer, path=["response"])

    @parametrize
    async def test_streaming_response_refresh_review(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.with_streaming_response.refresh_review(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_refresh_review(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.customers.with_raw_response.refresh_review(
                id="",
            )

    @parametrize
    async def test_method_unmasked(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerUnmaskedV1, customer, path=["response"])

    @parametrize
    async def test_method_unmasked_with_all_params(self, async_client: AsyncStraddle) -> None:
        customer = await async_client.customers.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CustomerUnmaskedV1, customer, path=["response"])

    @parametrize
    async def test_raw_response_unmasked(self, async_client: AsyncStraddle) -> None:
        response = await async_client.customers.with_raw_response.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerUnmaskedV1, customer, path=["response"])

    @parametrize
    async def test_streaming_response_unmasked(self, async_client: AsyncStraddle) -> None:
        async with async_client.customers.with_streaming_response.unmasked(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerUnmaskedV1, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_unmasked(self, async_client: AsyncStraddle) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.customers.with_raw_response.unmasked(
                id="",
            )
