# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .organizations import (
    OrganizationsResource,
    AsyncOrganizationsResource,
    OrganizationsResourceWithRawResponse,
    AsyncOrganizationsResourceWithRawResponse,
    OrganizationsResourceWithStreamingResponse,
    AsyncOrganizationsResourceWithStreamingResponse,
)
from .representatives import (
    RepresentativesResource,
    AsyncRepresentativesResource,
    RepresentativesResourceWithRawResponse,
    AsyncRepresentativesResourceWithRawResponse,
    RepresentativesResourceWithStreamingResponse,
    AsyncRepresentativesResourceWithStreamingResponse,
)
from .accounts.accounts import (
    AccountsResource,
    AsyncAccountsResource,
    AccountsResourceWithRawResponse,
    AsyncAccountsResourceWithRawResponse,
    AccountsResourceWithStreamingResponse,
    AsyncAccountsResourceWithStreamingResponse,
)
from .linked_bank_accounts import (
    LinkedBankAccountsResource,
    AsyncLinkedBankAccountsResource,
    LinkedBankAccountsResourceWithRawResponse,
    AsyncLinkedBankAccountsResourceWithRawResponse,
    LinkedBankAccountsResourceWithStreamingResponse,
    AsyncLinkedBankAccountsResourceWithStreamingResponse,
)

__all__ = ["EmbedResource", "AsyncEmbedResource"]


class EmbedResource(SyncAPIResource):
    @cached_property
    def accounts(self) -> AccountsResource:
        return AccountsResource(self._client)

    @cached_property
    def linked_bank_accounts(self) -> LinkedBankAccountsResource:
        return LinkedBankAccountsResource(self._client)

    @cached_property
    def organizations(self) -> OrganizationsResource:
        return OrganizationsResource(self._client)

    @cached_property
    def representatives(self) -> RepresentativesResource:
        return RepresentativesResource(self._client)

    @cached_property
    def with_raw_response(self) -> EmbedResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return EmbedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EmbedResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return EmbedResourceWithStreamingResponse(self)


class AsyncEmbedResource(AsyncAPIResource):
    @cached_property
    def accounts(self) -> AsyncAccountsResource:
        return AsyncAccountsResource(self._client)

    @cached_property
    def linked_bank_accounts(self) -> AsyncLinkedBankAccountsResource:
        return AsyncLinkedBankAccountsResource(self._client)

    @cached_property
    def organizations(self) -> AsyncOrganizationsResource:
        return AsyncOrganizationsResource(self._client)

    @cached_property
    def representatives(self) -> AsyncRepresentativesResource:
        return AsyncRepresentativesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEmbedResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEmbedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEmbedResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncEmbedResourceWithStreamingResponse(self)


class EmbedResourceWithRawResponse:
    def __init__(self, embed: EmbedResource) -> None:
        self._embed = embed

    @cached_property
    def accounts(self) -> AccountsResourceWithRawResponse:
        return AccountsResourceWithRawResponse(self._embed.accounts)

    @cached_property
    def linked_bank_accounts(self) -> LinkedBankAccountsResourceWithRawResponse:
        return LinkedBankAccountsResourceWithRawResponse(self._embed.linked_bank_accounts)

    @cached_property
    def organizations(self) -> OrganizationsResourceWithRawResponse:
        return OrganizationsResourceWithRawResponse(self._embed.organizations)

    @cached_property
    def representatives(self) -> RepresentativesResourceWithRawResponse:
        return RepresentativesResourceWithRawResponse(self._embed.representatives)


class AsyncEmbedResourceWithRawResponse:
    def __init__(self, embed: AsyncEmbedResource) -> None:
        self._embed = embed

    @cached_property
    def accounts(self) -> AsyncAccountsResourceWithRawResponse:
        return AsyncAccountsResourceWithRawResponse(self._embed.accounts)

    @cached_property
    def linked_bank_accounts(self) -> AsyncLinkedBankAccountsResourceWithRawResponse:
        return AsyncLinkedBankAccountsResourceWithRawResponse(self._embed.linked_bank_accounts)

    @cached_property
    def organizations(self) -> AsyncOrganizationsResourceWithRawResponse:
        return AsyncOrganizationsResourceWithRawResponse(self._embed.organizations)

    @cached_property
    def representatives(self) -> AsyncRepresentativesResourceWithRawResponse:
        return AsyncRepresentativesResourceWithRawResponse(self._embed.representatives)


class EmbedResourceWithStreamingResponse:
    def __init__(self, embed: EmbedResource) -> None:
        self._embed = embed

    @cached_property
    def accounts(self) -> AccountsResourceWithStreamingResponse:
        return AccountsResourceWithStreamingResponse(self._embed.accounts)

    @cached_property
    def linked_bank_accounts(self) -> LinkedBankAccountsResourceWithStreamingResponse:
        return LinkedBankAccountsResourceWithStreamingResponse(self._embed.linked_bank_accounts)

    @cached_property
    def organizations(self) -> OrganizationsResourceWithStreamingResponse:
        return OrganizationsResourceWithStreamingResponse(self._embed.organizations)

    @cached_property
    def representatives(self) -> RepresentativesResourceWithStreamingResponse:
        return RepresentativesResourceWithStreamingResponse(self._embed.representatives)


class AsyncEmbedResourceWithStreamingResponse:
    def __init__(self, embed: AsyncEmbedResource) -> None:
        self._embed = embed

    @cached_property
    def accounts(self) -> AsyncAccountsResourceWithStreamingResponse:
        return AsyncAccountsResourceWithStreamingResponse(self._embed.accounts)

    @cached_property
    def linked_bank_accounts(self) -> AsyncLinkedBankAccountsResourceWithStreamingResponse:
        return AsyncLinkedBankAccountsResourceWithStreamingResponse(self._embed.linked_bank_accounts)

    @cached_property
    def organizations(self) -> AsyncOrganizationsResourceWithStreamingResponse:
        return AsyncOrganizationsResourceWithStreamingResponse(self._embed.organizations)

    @cached_property
    def representatives(self) -> AsyncRepresentativesResourceWithStreamingResponse:
        return AsyncRepresentativesResourceWithStreamingResponse(self._embed.representatives)
