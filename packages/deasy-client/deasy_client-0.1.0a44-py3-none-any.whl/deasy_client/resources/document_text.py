# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ..types import document_text_get_params
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
from ..types.document_text_get_response import DocumentTextGetResponse

__all__ = ["DocumentTextResource", "AsyncDocumentTextResource"]


class DocumentTextResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentTextResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return DocumentTextResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentTextResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return DocumentTextResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        data_connector_name: str,
        file_names: List[str],
        chunk_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTextGetResponse:
        """
        Retrieve the raw text content for specified documents from the vector database

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/data/document_text",
            body=maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "file_names": file_names,
                    "chunk_ids": chunk_ids,
                },
                document_text_get_params.DocumentTextGetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentTextGetResponse,
        )


class AsyncDocumentTextResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentTextResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentTextResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentTextResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncDocumentTextResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        data_connector_name: str,
        file_names: List[str],
        chunk_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentTextGetResponse:
        """
        Retrieve the raw text content for specified documents from the vector database

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/data/document_text",
            body=await async_maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "file_names": file_names,
                    "chunk_ids": chunk_ids,
                },
                document_text_get_params.DocumentTextGetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentTextGetResponse,
        )


class DocumentTextResourceWithRawResponse:
    def __init__(self, document_text: DocumentTextResource) -> None:
        self._document_text = document_text

        self.get = to_raw_response_wrapper(
            document_text.get,
        )


class AsyncDocumentTextResourceWithRawResponse:
    def __init__(self, document_text: AsyncDocumentTextResource) -> None:
        self._document_text = document_text

        self.get = async_to_raw_response_wrapper(
            document_text.get,
        )


class DocumentTextResourceWithStreamingResponse:
    def __init__(self, document_text: DocumentTextResource) -> None:
        self._document_text = document_text

        self.get = to_streamed_response_wrapper(
            document_text.get,
        )


class AsyncDocumentTextResourceWithStreamingResponse:
    def __init__(self, document_text: AsyncDocumentTextResource) -> None:
        self._document_text = document_text

        self.get = async_to_streamed_response_wrapper(
            document_text.get,
        )
