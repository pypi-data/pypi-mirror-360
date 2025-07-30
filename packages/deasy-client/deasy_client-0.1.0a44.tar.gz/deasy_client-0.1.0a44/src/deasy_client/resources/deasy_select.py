# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal

import httpx

from ..types import deasy_select_query_params
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

__all__ = ["DeasySelectResource", "AsyncDeasySelectResource"]


class DeasySelectResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DeasySelectResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return DeasySelectResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeasySelectResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return DeasySelectResourceWithStreamingResponse(self)

    def query(
        self,
        *,
        data_connector_name: str,
        query: str,
        banned_filters: Optional[Dict[str, List[Union[str, float]]]] | NotGiven = NOT_GIVEN,
        file_hybrid_search_boost: Optional[float] | NotGiven = NOT_GIVEN,
        metadata_hybrid_search: Optional[bool] | NotGiven = NOT_GIVEN,
        metadata_hybrid_search_boost: Optional[float] | NotGiven = NOT_GIVEN,
        metadata_reranker: Optional[bool] | NotGiven = NOT_GIVEN,
        return_only_query: Optional[bool] | NotGiven = NOT_GIVEN,
        tag_distributions: Optional[Dict[str, deasy_select_query_params.TagDistributions]] | NotGiven = NOT_GIVEN,
        tag_level: Optional[Literal["chunk", "both"]] | NotGiven = NOT_GIVEN,
        tag_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        tag_schemas: Optional[Iterable[deasy_select_query_params.TagSchema]] | NotGiven = NOT_GIVEN,
        top_k: Optional[int] | NotGiven = NOT_GIVEN,
        with_text: Optional[bool] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Deasy Select Query

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/deasy_select/query",
            body=maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "query": query,
                    "banned_filters": banned_filters,
                    "file_hybrid_search_boost": file_hybrid_search_boost,
                    "metadata_hybrid_search": metadata_hybrid_search,
                    "metadata_hybrid_search_boost": metadata_hybrid_search_boost,
                    "metadata_reranker": metadata_reranker,
                    "return_only_query": return_only_query,
                    "tag_distributions": tag_distributions,
                    "tag_level": tag_level,
                    "tag_names": tag_names,
                    "tag_schemas": tag_schemas,
                    "top_k": top_k,
                    "with_text": with_text,
                },
                deasy_select_query_params.DeasySelectQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncDeasySelectResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDeasySelectResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncDeasySelectResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeasySelectResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncDeasySelectResourceWithStreamingResponse(self)

    async def query(
        self,
        *,
        data_connector_name: str,
        query: str,
        banned_filters: Optional[Dict[str, List[Union[str, float]]]] | NotGiven = NOT_GIVEN,
        file_hybrid_search_boost: Optional[float] | NotGiven = NOT_GIVEN,
        metadata_hybrid_search: Optional[bool] | NotGiven = NOT_GIVEN,
        metadata_hybrid_search_boost: Optional[float] | NotGiven = NOT_GIVEN,
        metadata_reranker: Optional[bool] | NotGiven = NOT_GIVEN,
        return_only_query: Optional[bool] | NotGiven = NOT_GIVEN,
        tag_distributions: Optional[Dict[str, deasy_select_query_params.TagDistributions]] | NotGiven = NOT_GIVEN,
        tag_level: Optional[Literal["chunk", "both"]] | NotGiven = NOT_GIVEN,
        tag_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        tag_schemas: Optional[Iterable[deasy_select_query_params.TagSchema]] | NotGiven = NOT_GIVEN,
        top_k: Optional[int] | NotGiven = NOT_GIVEN,
        with_text: Optional[bool] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Deasy Select Query

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/deasy_select/query",
            body=await async_maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "query": query,
                    "banned_filters": banned_filters,
                    "file_hybrid_search_boost": file_hybrid_search_boost,
                    "metadata_hybrid_search": metadata_hybrid_search,
                    "metadata_hybrid_search_boost": metadata_hybrid_search_boost,
                    "metadata_reranker": metadata_reranker,
                    "return_only_query": return_only_query,
                    "tag_distributions": tag_distributions,
                    "tag_level": tag_level,
                    "tag_names": tag_names,
                    "tag_schemas": tag_schemas,
                    "top_k": top_k,
                    "with_text": with_text,
                },
                deasy_select_query_params.DeasySelectQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class DeasySelectResourceWithRawResponse:
    def __init__(self, deasy_select: DeasySelectResource) -> None:
        self._deasy_select = deasy_select

        self.query = to_raw_response_wrapper(
            deasy_select.query,
        )


class AsyncDeasySelectResourceWithRawResponse:
    def __init__(self, deasy_select: AsyncDeasySelectResource) -> None:
        self._deasy_select = deasy_select

        self.query = async_to_raw_response_wrapper(
            deasy_select.query,
        )


class DeasySelectResourceWithStreamingResponse:
    def __init__(self, deasy_select: DeasySelectResource) -> None:
        self._deasy_select = deasy_select

        self.query = to_streamed_response_wrapper(
            deasy_select.query,
        )


class AsyncDeasySelectResourceWithStreamingResponse:
    def __init__(self, deasy_select: AsyncDeasySelectResource) -> None:
        self._deasy_select = deasy_select

        self.query = async_to_streamed_response_wrapper(
            deasy_select.query,
        )
