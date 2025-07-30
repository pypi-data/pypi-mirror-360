# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional

import httpx

from ..types import classify_bulk_classify_params
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
from ..types.condition_input_param import ConditionInputParam
from ..types.classify_bulk_classify_response import ClassifyBulkClassifyResponse

__all__ = ["ClassifyBulkResource", "AsyncClassifyBulkResource"]


class ClassifyBulkResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClassifyBulkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return ClassifyBulkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClassifyBulkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return ClassifyBulkResourceWithStreamingResponse(self)

    def classify(
        self,
        *,
        data_connector_name: str,
        conditions: Optional[ConditionInputParam] | NotGiven = NOT_GIVEN,
        dataslice_id: Optional[str] | NotGiven = NOT_GIVEN,
        hierarchy_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        hierarchy_name: Optional[str] | NotGiven = NOT_GIVEN,
        job_id: Optional[str] | NotGiven = NOT_GIVEN,
        llm_profile_name: Optional[str] | NotGiven = NOT_GIVEN,
        overwrite: bool | NotGiven = NOT_GIVEN,
        tag_datas: Optional[Dict[str, classify_bulk_classify_params.TagDatas]] | NotGiven = NOT_GIVEN,
        tag_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        total_data_sets: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClassifyBulkClassifyResponse:
        """
        Classify all files in data source in batches with the provided tags

        Attributes:

            data_connector_name: The name of the vdb profile to use for classification.
            llm_profile_name: The name of the llm profile to use for classification.
            total_data_sets: The total number of files to classify.
            tag_names: The names of the tags to use for classification if tag datas are not provided.
            tag_datas: The data of the tags to use for classification.
            overwrite: Whether to overwrite existing tags.
            hierarchy_name: The name of the graph to use for classification if hierarchy data is not provided.
            hierarchy_data: The data of the graph to use for classification.
            dataslice_id: The id of the dataslice to use for classification file filtering.
            conditions: The conditions to use for classification file filtering.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/classify_bulk",
            body=maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "conditions": conditions,
                    "dataslice_id": dataslice_id,
                    "hierarchy_data": hierarchy_data,
                    "hierarchy_name": hierarchy_name,
                    "job_id": job_id,
                    "llm_profile_name": llm_profile_name,
                    "overwrite": overwrite,
                    "tag_datas": tag_datas,
                    "tag_names": tag_names,
                    "total_data_sets": total_data_sets,
                },
                classify_bulk_classify_params.ClassifyBulkClassifyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClassifyBulkClassifyResponse,
        )


class AsyncClassifyBulkResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClassifyBulkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncClassifyBulkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClassifyBulkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncClassifyBulkResourceWithStreamingResponse(self)

    async def classify(
        self,
        *,
        data_connector_name: str,
        conditions: Optional[ConditionInputParam] | NotGiven = NOT_GIVEN,
        dataslice_id: Optional[str] | NotGiven = NOT_GIVEN,
        hierarchy_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        hierarchy_name: Optional[str] | NotGiven = NOT_GIVEN,
        job_id: Optional[str] | NotGiven = NOT_GIVEN,
        llm_profile_name: Optional[str] | NotGiven = NOT_GIVEN,
        overwrite: bool | NotGiven = NOT_GIVEN,
        tag_datas: Optional[Dict[str, classify_bulk_classify_params.TagDatas]] | NotGiven = NOT_GIVEN,
        tag_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        total_data_sets: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClassifyBulkClassifyResponse:
        """
        Classify all files in data source in batches with the provided tags

        Attributes:

            data_connector_name: The name of the vdb profile to use for classification.
            llm_profile_name: The name of the llm profile to use for classification.
            total_data_sets: The total number of files to classify.
            tag_names: The names of the tags to use for classification if tag datas are not provided.
            tag_datas: The data of the tags to use for classification.
            overwrite: Whether to overwrite existing tags.
            hierarchy_name: The name of the graph to use for classification if hierarchy data is not provided.
            hierarchy_data: The data of the graph to use for classification.
            dataslice_id: The id of the dataslice to use for classification file filtering.
            conditions: The conditions to use for classification file filtering.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/classify_bulk",
            body=await async_maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "conditions": conditions,
                    "dataslice_id": dataslice_id,
                    "hierarchy_data": hierarchy_data,
                    "hierarchy_name": hierarchy_name,
                    "job_id": job_id,
                    "llm_profile_name": llm_profile_name,
                    "overwrite": overwrite,
                    "tag_datas": tag_datas,
                    "tag_names": tag_names,
                    "total_data_sets": total_data_sets,
                },
                classify_bulk_classify_params.ClassifyBulkClassifyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClassifyBulkClassifyResponse,
        )


class ClassifyBulkResourceWithRawResponse:
    def __init__(self, classify_bulk: ClassifyBulkResource) -> None:
        self._classify_bulk = classify_bulk

        self.classify = to_raw_response_wrapper(
            classify_bulk.classify,
        )


class AsyncClassifyBulkResourceWithRawResponse:
    def __init__(self, classify_bulk: AsyncClassifyBulkResource) -> None:
        self._classify_bulk = classify_bulk

        self.classify = async_to_raw_response_wrapper(
            classify_bulk.classify,
        )


class ClassifyBulkResourceWithStreamingResponse:
    def __init__(self, classify_bulk: ClassifyBulkResource) -> None:
        self._classify_bulk = classify_bulk

        self.classify = to_streamed_response_wrapper(
            classify_bulk.classify,
        )


class AsyncClassifyBulkResourceWithStreamingResponse:
    def __init__(self, classify_bulk: AsyncClassifyBulkResource) -> None:
        self._classify_bulk = classify_bulk

        self.classify = async_to_streamed_response_wrapper(
            classify_bulk.classify,
        )
