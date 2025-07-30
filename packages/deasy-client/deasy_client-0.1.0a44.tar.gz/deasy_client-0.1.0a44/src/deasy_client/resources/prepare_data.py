# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import prepare_data_create_params
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
from ..types.prepare_data_create_response import PrepareDataCreateResponse

__all__ = ["PrepareDataResource", "AsyncPrepareDataResource"]


class PrepareDataResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PrepareDataResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return PrepareDataResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PrepareDataResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return PrepareDataResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        data_connector_name: str,
        job_id: Optional[str] | NotGiven = NOT_GIVEN,
        llm_profile_name: Optional[str] | NotGiven = NOT_GIVEN,
        total_data_sets: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PrepareDataCreateResponse:
        """
        Prepare data to enable Deasy auto-suggestions

        Attributes:

            data_connector_name: The name of the vdb profile to use for classification.
            llm_profile_name: The name of the llm profile to use for classification.
            total_data_sets: The total number of files that will be prepared.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/prepare_data",
            body=maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "job_id": job_id,
                    "llm_profile_name": llm_profile_name,
                    "total_data_sets": total_data_sets,
                },
                prepare_data_create_params.PrepareDataCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PrepareDataCreateResponse,
        )


class AsyncPrepareDataResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPrepareDataResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncPrepareDataResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPrepareDataResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncPrepareDataResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        data_connector_name: str,
        job_id: Optional[str] | NotGiven = NOT_GIVEN,
        llm_profile_name: Optional[str] | NotGiven = NOT_GIVEN,
        total_data_sets: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PrepareDataCreateResponse:
        """
        Prepare data to enable Deasy auto-suggestions

        Attributes:

            data_connector_name: The name of the vdb profile to use for classification.
            llm_profile_name: The name of the llm profile to use for classification.
            total_data_sets: The total number of files that will be prepared.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/prepare_data",
            body=await async_maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "job_id": job_id,
                    "llm_profile_name": llm_profile_name,
                    "total_data_sets": total_data_sets,
                },
                prepare_data_create_params.PrepareDataCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PrepareDataCreateResponse,
        )


class PrepareDataResourceWithRawResponse:
    def __init__(self, prepare_data: PrepareDataResource) -> None:
        self._prepare_data = prepare_data

        self.create = to_raw_response_wrapper(
            prepare_data.create,
        )


class AsyncPrepareDataResourceWithRawResponse:
    def __init__(self, prepare_data: AsyncPrepareDataResource) -> None:
        self._prepare_data = prepare_data

        self.create = async_to_raw_response_wrapper(
            prepare_data.create,
        )


class PrepareDataResourceWithStreamingResponse:
    def __init__(self, prepare_data: PrepareDataResource) -> None:
        self._prepare_data = prepare_data

        self.create = to_streamed_response_wrapper(
            prepare_data.create,
        )


class AsyncPrepareDataResourceWithStreamingResponse:
    def __init__(self, prepare_data: AsyncPrepareDataResource) -> None:
        self._prepare_data = prepare_data

        self.create = async_to_streamed_response_wrapper(
            prepare_data.create,
        )
