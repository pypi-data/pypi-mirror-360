# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    vdb_connector_create_params,
    vdb_connector_delete_params,
    vdb_connector_update_params,
    vdb_connector_get_delete_stats_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.connector_response import ConnectorResponse
from ..types.list_vdb_connector import ListVdbConnector
from ..types.vdb_connector_get_delete_stats_response import VdbConnectorGetDeleteStatsResponse

__all__ = ["VdbConnectorResource", "AsyncVdbConnectorResource"]


class VdbConnectorResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> VdbConnectorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return VdbConnectorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VdbConnectorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return VdbConnectorResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        connector_body: vdb_connector_create_params.ConnectorBody,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Create a new vdb connector

        Attributes:

            connector_name: The profile name of the connector to create.
            connector_body: The body of the connector to create.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/vdb_connector/create",
            body=maybe_transform(
                {
                    "connector_body": connector_body,
                    "connector_name": connector_name,
                },
                vdb_connector_create_params.VdbConnectorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )

    def update(
        self,
        *,
        connector_body: vdb_connector_update_params.ConnectorBody,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Update a vdb connector

        Attributes:

            connector_name: The profile name of the connector to update.
            connector_body: The body of the connector to update.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/vdb_connector/update",
            body=maybe_transform(
                {
                    "connector_body": connector_body,
                    "connector_name": connector_name,
                },
                vdb_connector_update_params.VdbConnectorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListVdbConnector:
        """List all the vdb connectors"""
        return self._post(
            "/vdb_connector/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListVdbConnector,
        )

    def delete(
        self,
        *,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Delete a vdb connector

        Attributes:

            connector_name: The profile name of the connector to delete.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/vdb_connector/delete",
            body=maybe_transform(
                {"connector_name": connector_name}, vdb_connector_delete_params.VdbConnectorDeleteParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )

    def get_delete_stats(
        self,
        *,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VdbConnectorGetDeleteStatsResponse:
        """
        Get tag delete stats of a vdb connector

        Attributes:

            connector_name: The profile name of the connector to get the delete stats for.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/vdb_connector/delete_stats",
            body=maybe_transform(
                {"connector_name": connector_name},
                vdb_connector_get_delete_stats_params.VdbConnectorGetDeleteStatsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VdbConnectorGetDeleteStatsResponse,
        )


class AsyncVdbConnectorResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncVdbConnectorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncVdbConnectorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVdbConnectorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncVdbConnectorResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        connector_body: vdb_connector_create_params.ConnectorBody,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Create a new vdb connector

        Attributes:

            connector_name: The profile name of the connector to create.
            connector_body: The body of the connector to create.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/vdb_connector/create",
            body=await async_maybe_transform(
                {
                    "connector_body": connector_body,
                    "connector_name": connector_name,
                },
                vdb_connector_create_params.VdbConnectorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )

    async def update(
        self,
        *,
        connector_body: vdb_connector_update_params.ConnectorBody,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Update a vdb connector

        Attributes:

            connector_name: The profile name of the connector to update.
            connector_body: The body of the connector to update.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/vdb_connector/update",
            body=await async_maybe_transform(
                {
                    "connector_body": connector_body,
                    "connector_name": connector_name,
                },
                vdb_connector_update_params.VdbConnectorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListVdbConnector:
        """List all the vdb connectors"""
        return await self._post(
            "/vdb_connector/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListVdbConnector,
        )

    async def delete(
        self,
        *,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Delete a vdb connector

        Attributes:

            connector_name: The profile name of the connector to delete.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/vdb_connector/delete",
            body=await async_maybe_transform(
                {"connector_name": connector_name}, vdb_connector_delete_params.VdbConnectorDeleteParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )

    async def get_delete_stats(
        self,
        *,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VdbConnectorGetDeleteStatsResponse:
        """
        Get tag delete stats of a vdb connector

        Attributes:

            connector_name: The profile name of the connector to get the delete stats for.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/vdb_connector/delete_stats",
            body=await async_maybe_transform(
                {"connector_name": connector_name},
                vdb_connector_get_delete_stats_params.VdbConnectorGetDeleteStatsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VdbConnectorGetDeleteStatsResponse,
        )


class VdbConnectorResourceWithRawResponse:
    def __init__(self, vdb_connector: VdbConnectorResource) -> None:
        self._vdb_connector = vdb_connector

        self.create = to_raw_response_wrapper(
            vdb_connector.create,
        )
        self.update = to_raw_response_wrapper(
            vdb_connector.update,
        )
        self.list = to_raw_response_wrapper(
            vdb_connector.list,
        )
        self.delete = to_raw_response_wrapper(
            vdb_connector.delete,
        )
        self.get_delete_stats = to_raw_response_wrapper(
            vdb_connector.get_delete_stats,
        )


class AsyncVdbConnectorResourceWithRawResponse:
    def __init__(self, vdb_connector: AsyncVdbConnectorResource) -> None:
        self._vdb_connector = vdb_connector

        self.create = async_to_raw_response_wrapper(
            vdb_connector.create,
        )
        self.update = async_to_raw_response_wrapper(
            vdb_connector.update,
        )
        self.list = async_to_raw_response_wrapper(
            vdb_connector.list,
        )
        self.delete = async_to_raw_response_wrapper(
            vdb_connector.delete,
        )
        self.get_delete_stats = async_to_raw_response_wrapper(
            vdb_connector.get_delete_stats,
        )


class VdbConnectorResourceWithStreamingResponse:
    def __init__(self, vdb_connector: VdbConnectorResource) -> None:
        self._vdb_connector = vdb_connector

        self.create = to_streamed_response_wrapper(
            vdb_connector.create,
        )
        self.update = to_streamed_response_wrapper(
            vdb_connector.update,
        )
        self.list = to_streamed_response_wrapper(
            vdb_connector.list,
        )
        self.delete = to_streamed_response_wrapper(
            vdb_connector.delete,
        )
        self.get_delete_stats = to_streamed_response_wrapper(
            vdb_connector.get_delete_stats,
        )


class AsyncVdbConnectorResourceWithStreamingResponse:
    def __init__(self, vdb_connector: AsyncVdbConnectorResource) -> None:
        self._vdb_connector = vdb_connector

        self.create = async_to_streamed_response_wrapper(
            vdb_connector.create,
        )
        self.update = async_to_streamed_response_wrapper(
            vdb_connector.update,
        )
        self.list = async_to_streamed_response_wrapper(
            vdb_connector.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            vdb_connector.delete,
        )
        self.get_delete_stats = async_to_streamed_response_wrapper(
            vdb_connector.get_delete_stats,
        )
