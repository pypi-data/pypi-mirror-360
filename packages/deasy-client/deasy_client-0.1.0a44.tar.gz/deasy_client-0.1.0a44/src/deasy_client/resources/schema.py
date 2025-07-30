# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional

import httpx

from ..types import (
    schema_list_params,
    schema_create_params,
    schema_delete_params,
    schema_update_params,
    schema_upsert_params,
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
from ..types.schema_list_response import SchemaListResponse
from ..types.schema_operation_response import SchemaOperationResponse

__all__ = ["SchemaResource", "AsyncSchemaResource"]


class SchemaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SchemaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return SchemaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SchemaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return SchemaResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        schema_name: str,
        schema_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        schema_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaOperationResponse:
        """
        Create a new graph.

        Attributes:

            schema_name: The name of the schema to create.
            schema_description: The description of the schema to create.
            schema_data: The data of the schema to create.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/schema/create",
            body=maybe_transform(
                {
                    "schema_name": schema_name,
                    "schema_data": schema_data,
                    "schema_description": schema_description,
                },
                schema_create_params.SchemaCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaOperationResponse,
        )

    def update(
        self,
        *,
        schema_name: str,
        schema_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        schema_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaOperationResponse:
        """
        Update a graph in the database.

        Attributes:

            schema_name: The name of the schema to update.
            schema_description: The description of the schema to update.
            schema_data: The data of the schema to update.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/schema/update",
            body=maybe_transform(
                {
                    "schema_name": schema_name,
                    "schema_data": schema_data,
                    "schema_description": schema_description,
                },
                schema_update_params.SchemaUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaOperationResponse,
        )

    def list(
        self,
        *,
        schema_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaListResponse:
        """
        List all schemas for the authenticated user.

        Attributes:

            schema_ids: The ids of the schemas to retrieve.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/schema/list",
            body=maybe_transform({"schema_ids": schema_ids}, schema_list_params.SchemaListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaListResponse,
        )

    def delete(
        self,
        *,
        schema_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaOperationResponse:
        """
        Delete a schema by name.

        Attributes:

            schema_name: The name of the schema to delete.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/schema/delete",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"schema_name": schema_name}, schema_delete_params.SchemaDeleteParams),
            ),
            cast_to=SchemaOperationResponse,
        )

    def upsert(
        self,
        *,
        schema_name: str,
        new_schema_name: Optional[str] | NotGiven = NOT_GIVEN,
        schema_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        schema_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaOperationResponse:
        """
        Upsert a schema in the database.

        Attributes:

            schema_name: The stored name of the schema to upsert.
            new_schema_name: The new name of the schema to upsert.
            schema_description: The description of the schema to upsert.
            schema_data: The data of the schema to upsert.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/schema/upsert",
            body=maybe_transform(
                {
                    "schema_name": schema_name,
                    "new_schema_name": new_schema_name,
                    "schema_data": schema_data,
                    "schema_description": schema_description,
                },
                schema_upsert_params.SchemaUpsertParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaOperationResponse,
        )


class AsyncSchemaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSchemaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncSchemaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSchemaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncSchemaResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        schema_name: str,
        schema_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        schema_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaOperationResponse:
        """
        Create a new graph.

        Attributes:

            schema_name: The name of the schema to create.
            schema_description: The description of the schema to create.
            schema_data: The data of the schema to create.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/schema/create",
            body=await async_maybe_transform(
                {
                    "schema_name": schema_name,
                    "schema_data": schema_data,
                    "schema_description": schema_description,
                },
                schema_create_params.SchemaCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaOperationResponse,
        )

    async def update(
        self,
        *,
        schema_name: str,
        schema_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        schema_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaOperationResponse:
        """
        Update a graph in the database.

        Attributes:

            schema_name: The name of the schema to update.
            schema_description: The description of the schema to update.
            schema_data: The data of the schema to update.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/schema/update",
            body=await async_maybe_transform(
                {
                    "schema_name": schema_name,
                    "schema_data": schema_data,
                    "schema_description": schema_description,
                },
                schema_update_params.SchemaUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaOperationResponse,
        )

    async def list(
        self,
        *,
        schema_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaListResponse:
        """
        List all schemas for the authenticated user.

        Attributes:

            schema_ids: The ids of the schemas to retrieve.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/schema/list",
            body=await async_maybe_transform({"schema_ids": schema_ids}, schema_list_params.SchemaListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaListResponse,
        )

    async def delete(
        self,
        *,
        schema_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaOperationResponse:
        """
        Delete a schema by name.

        Attributes:

            schema_name: The name of the schema to delete.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/schema/delete",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"schema_name": schema_name}, schema_delete_params.SchemaDeleteParams
                ),
            ),
            cast_to=SchemaOperationResponse,
        )

    async def upsert(
        self,
        *,
        schema_name: str,
        new_schema_name: Optional[str] | NotGiven = NOT_GIVEN,
        schema_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        schema_description: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SchemaOperationResponse:
        """
        Upsert a schema in the database.

        Attributes:

            schema_name: The stored name of the schema to upsert.
            new_schema_name: The new name of the schema to upsert.
            schema_description: The description of the schema to upsert.
            schema_data: The data of the schema to upsert.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/schema/upsert",
            body=await async_maybe_transform(
                {
                    "schema_name": schema_name,
                    "new_schema_name": new_schema_name,
                    "schema_data": schema_data,
                    "schema_description": schema_description,
                },
                schema_upsert_params.SchemaUpsertParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaOperationResponse,
        )


class SchemaResourceWithRawResponse:
    def __init__(self, schema: SchemaResource) -> None:
        self._schema = schema

        self.create = to_raw_response_wrapper(
            schema.create,
        )
        self.update = to_raw_response_wrapper(
            schema.update,
        )
        self.list = to_raw_response_wrapper(
            schema.list,
        )
        self.delete = to_raw_response_wrapper(
            schema.delete,
        )
        self.upsert = to_raw_response_wrapper(
            schema.upsert,
        )


class AsyncSchemaResourceWithRawResponse:
    def __init__(self, schema: AsyncSchemaResource) -> None:
        self._schema = schema

        self.create = async_to_raw_response_wrapper(
            schema.create,
        )
        self.update = async_to_raw_response_wrapper(
            schema.update,
        )
        self.list = async_to_raw_response_wrapper(
            schema.list,
        )
        self.delete = async_to_raw_response_wrapper(
            schema.delete,
        )
        self.upsert = async_to_raw_response_wrapper(
            schema.upsert,
        )


class SchemaResourceWithStreamingResponse:
    def __init__(self, schema: SchemaResource) -> None:
        self._schema = schema

        self.create = to_streamed_response_wrapper(
            schema.create,
        )
        self.update = to_streamed_response_wrapper(
            schema.update,
        )
        self.list = to_streamed_response_wrapper(
            schema.list,
        )
        self.delete = to_streamed_response_wrapper(
            schema.delete,
        )
        self.upsert = to_streamed_response_wrapper(
            schema.upsert,
        )


class AsyncSchemaResourceWithStreamingResponse:
    def __init__(self, schema: AsyncSchemaResource) -> None:
        self._schema = schema

        self.create = async_to_streamed_response_wrapper(
            schema.create,
        )
        self.update = async_to_streamed_response_wrapper(
            schema.update,
        )
        self.list = async_to_streamed_response_wrapper(
            schema.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            schema.delete,
        )
        self.upsert = async_to_streamed_response_wrapper(
            schema.upsert,
        )
