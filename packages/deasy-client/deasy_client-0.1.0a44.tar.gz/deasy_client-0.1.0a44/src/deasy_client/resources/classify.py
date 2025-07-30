# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional

import httpx

from ..types import classify_classify_files_params
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
from ..types.classify_classify_files_response import ClassifyClassifyFilesResponse

__all__ = ["ClassifyResource", "AsyncClassifyResource"]


class ClassifyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClassifyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return ClassifyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClassifyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return ClassifyResourceWithStreamingResponse(self)

    def classify_files(
        self,
        *,
        data_connector_name: str,
        dataslice_id: Optional[str] | NotGiven = NOT_GIVEN,
        file_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        hierarchy_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        hierarchy_name: Optional[str] | NotGiven = NOT_GIVEN,
        job_id: Optional[str] | NotGiven = NOT_GIVEN,
        llm_profile_name: Optional[str] | NotGiven = NOT_GIVEN,
        overwrite: bool | NotGiven = NOT_GIVEN,
        soft_run: bool | NotGiven = NOT_GIVEN,
        tag_datas: Optional[Dict[str, classify_classify_files_params.TagDatas]] | NotGiven = NOT_GIVEN,
        tag_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClassifyClassifyFilesResponse:
        """
        Classify files specified in the request with the provided tags

        Attributes:

            data_connector_name: The name of the vdb profile to use for classification.
            llm_profile_name: The name of the llm profile to use for classification.
            file_names: The names of the files to classify.
            tag_names: The names of the tags to use for classification if tag datas are not provided.
            tag_datas: The data of the tags to use for classification.
            overwrite: Whether to overwrite existing tags.
            hierarchy_name: The name of the graph to use for classification if hierarchy data is not provided.
            hierarchy_data: The data of the graph to use for classification.
            dataslice_id: The id of the dataslice to use for classification file filtering.
            soft_run: If true, the classification will not save to Deasy and will attempt to return the results.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/classify",
            body=maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "dataslice_id": dataslice_id,
                    "file_names": file_names,
                    "hierarchy_data": hierarchy_data,
                    "hierarchy_name": hierarchy_name,
                    "job_id": job_id,
                    "llm_profile_name": llm_profile_name,
                    "overwrite": overwrite,
                    "soft_run": soft_run,
                    "tag_datas": tag_datas,
                    "tag_names": tag_names,
                },
                classify_classify_files_params.ClassifyClassifyFilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClassifyClassifyFilesResponse,
        )


class AsyncClassifyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClassifyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncClassifyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClassifyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncClassifyResourceWithStreamingResponse(self)

    async def classify_files(
        self,
        *,
        data_connector_name: str,
        dataslice_id: Optional[str] | NotGiven = NOT_GIVEN,
        file_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        hierarchy_data: Optional[Dict[str, object]] | NotGiven = NOT_GIVEN,
        hierarchy_name: Optional[str] | NotGiven = NOT_GIVEN,
        job_id: Optional[str] | NotGiven = NOT_GIVEN,
        llm_profile_name: Optional[str] | NotGiven = NOT_GIVEN,
        overwrite: bool | NotGiven = NOT_GIVEN,
        soft_run: bool | NotGiven = NOT_GIVEN,
        tag_datas: Optional[Dict[str, classify_classify_files_params.TagDatas]] | NotGiven = NOT_GIVEN,
        tag_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClassifyClassifyFilesResponse:
        """
        Classify files specified in the request with the provided tags

        Attributes:

            data_connector_name: The name of the vdb profile to use for classification.
            llm_profile_name: The name of the llm profile to use for classification.
            file_names: The names of the files to classify.
            tag_names: The names of the tags to use for classification if tag datas are not provided.
            tag_datas: The data of the tags to use for classification.
            overwrite: Whether to overwrite existing tags.
            hierarchy_name: The name of the graph to use for classification if hierarchy data is not provided.
            hierarchy_data: The data of the graph to use for classification.
            dataslice_id: The id of the dataslice to use for classification file filtering.
            soft_run: If true, the classification will not save to Deasy and will attempt to return the results.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/classify",
            body=await async_maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "dataslice_id": dataslice_id,
                    "file_names": file_names,
                    "hierarchy_data": hierarchy_data,
                    "hierarchy_name": hierarchy_name,
                    "job_id": job_id,
                    "llm_profile_name": llm_profile_name,
                    "overwrite": overwrite,
                    "soft_run": soft_run,
                    "tag_datas": tag_datas,
                    "tag_names": tag_names,
                },
                classify_classify_files_params.ClassifyClassifyFilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClassifyClassifyFilesResponse,
        )


class ClassifyResourceWithRawResponse:
    def __init__(self, classify: ClassifyResource) -> None:
        self._classify = classify

        self.classify_files = to_raw_response_wrapper(
            classify.classify_files,
        )


class AsyncClassifyResourceWithRawResponse:
    def __init__(self, classify: AsyncClassifyResource) -> None:
        self._classify = classify

        self.classify_files = async_to_raw_response_wrapper(
            classify.classify_files,
        )


class ClassifyResourceWithStreamingResponse:
    def __init__(self, classify: ClassifyResource) -> None:
        self._classify = classify

        self.classify_files = to_streamed_response_wrapper(
            classify.classify_files,
        )


class AsyncClassifyResourceWithStreamingResponse:
    def __init__(self, classify: AsyncClassifyResource) -> None:
        self._classify = classify

        self.classify_files = async_to_streamed_response_wrapper(
            classify.classify_files,
        )
