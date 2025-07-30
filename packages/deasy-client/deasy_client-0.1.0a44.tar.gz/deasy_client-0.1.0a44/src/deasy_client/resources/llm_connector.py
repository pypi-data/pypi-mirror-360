# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import llm_connector_create_params, llm_connector_delete_params, llm_connector_update_params
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
from ..types.openai_config_param import OpenAIConfigParam
from ..types.llm_connector_list_response import LlmConnectorListResponse

__all__ = ["LlmConnectorResource", "AsyncLlmConnectorResource"]


class LlmConnectorResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LlmConnectorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return LlmConnectorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LlmConnectorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return LlmConnectorResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        connector_body: OpenAIConfigParam,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Create a new llm connector

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
            "/llm_connector/create",
            body=maybe_transform(
                {
                    "connector_body": connector_body,
                    "connector_name": connector_name,
                },
                llm_connector_create_params.LlmConnectorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )

    def update(
        self,
        *,
        connector_body: OpenAIConfigParam,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Update a llm connector

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
            "/llm_connector/update",
            body=maybe_transform(
                {
                    "connector_body": connector_body,
                    "connector_name": connector_name,
                },
                llm_connector_update_params.LlmConnectorUpdateParams,
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
    ) -> LlmConnectorListResponse:
        """List all the llm connectors"""
        return self._post(
            "/llm_connector/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LlmConnectorListResponse,
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
        Delete a llm connector

        Attributes:

            connector_name: The profile name of the connector to delete.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/llm_connector/delete",
            body=maybe_transform(
                {"connector_name": connector_name}, llm_connector_delete_params.LlmConnectorDeleteParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )


class AsyncLlmConnectorResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLlmConnectorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncLlmConnectorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLlmConnectorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncLlmConnectorResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        connector_body: OpenAIConfigParam,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Create a new llm connector

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
            "/llm_connector/create",
            body=await async_maybe_transform(
                {
                    "connector_body": connector_body,
                    "connector_name": connector_name,
                },
                llm_connector_create_params.LlmConnectorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )

    async def update(
        self,
        *,
        connector_body: OpenAIConfigParam,
        connector_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectorResponse:
        """
        Update a llm connector

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
            "/llm_connector/update",
            body=await async_maybe_transform(
                {
                    "connector_body": connector_body,
                    "connector_name": connector_name,
                },
                llm_connector_update_params.LlmConnectorUpdateParams,
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
    ) -> LlmConnectorListResponse:
        """List all the llm connectors"""
        return await self._post(
            "/llm_connector/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LlmConnectorListResponse,
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
        Delete a llm connector

        Attributes:

            connector_name: The profile name of the connector to delete.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/llm_connector/delete",
            body=await async_maybe_transform(
                {"connector_name": connector_name}, llm_connector_delete_params.LlmConnectorDeleteParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectorResponse,
        )


class LlmConnectorResourceWithRawResponse:
    def __init__(self, llm_connector: LlmConnectorResource) -> None:
        self._llm_connector = llm_connector

        self.create = to_raw_response_wrapper(
            llm_connector.create,
        )
        self.update = to_raw_response_wrapper(
            llm_connector.update,
        )
        self.list = to_raw_response_wrapper(
            llm_connector.list,
        )
        self.delete = to_raw_response_wrapper(
            llm_connector.delete,
        )


class AsyncLlmConnectorResourceWithRawResponse:
    def __init__(self, llm_connector: AsyncLlmConnectorResource) -> None:
        self._llm_connector = llm_connector

        self.create = async_to_raw_response_wrapper(
            llm_connector.create,
        )
        self.update = async_to_raw_response_wrapper(
            llm_connector.update,
        )
        self.list = async_to_raw_response_wrapper(
            llm_connector.list,
        )
        self.delete = async_to_raw_response_wrapper(
            llm_connector.delete,
        )


class LlmConnectorResourceWithStreamingResponse:
    def __init__(self, llm_connector: LlmConnectorResource) -> None:
        self._llm_connector = llm_connector

        self.create = to_streamed_response_wrapper(
            llm_connector.create,
        )
        self.update = to_streamed_response_wrapper(
            llm_connector.update,
        )
        self.list = to_streamed_response_wrapper(
            llm_connector.list,
        )
        self.delete = to_streamed_response_wrapper(
            llm_connector.delete,
        )


class AsyncLlmConnectorResourceWithStreamingResponse:
    def __init__(self, llm_connector: AsyncLlmConnectorResource) -> None:
        self._llm_connector = llm_connector

        self.create = async_to_streamed_response_wrapper(
            llm_connector.create,
        )
        self.update = async_to_streamed_response_wrapper(
            llm_connector.update,
        )
        self.list = async_to_streamed_response_wrapper(
            llm_connector.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            llm_connector.delete,
        )
