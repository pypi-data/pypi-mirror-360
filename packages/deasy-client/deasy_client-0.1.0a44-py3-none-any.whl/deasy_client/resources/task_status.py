# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import task_status_task_status_params
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
from ..types.task_status_task_status_response import TaskStatusTaskStatusResponse

__all__ = ["TaskStatusResource", "AsyncTaskStatusResource"]


class TaskStatusResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TaskStatusResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return TaskStatusResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TaskStatusResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return TaskStatusResourceWithStreamingResponse(self)

    def task_status(
        self,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskStatusTaskStatusResponse:
        """
        Get Task Progress

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/progress_tracker/task_status",
            body=maybe_transform({"job_id": job_id}, task_status_task_status_params.TaskStatusTaskStatusParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskStatusTaskStatusResponse,
        )


class AsyncTaskStatusResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTaskStatusResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncTaskStatusResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTaskStatusResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncTaskStatusResourceWithStreamingResponse(self)

    async def task_status(
        self,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskStatusTaskStatusResponse:
        """
        Get Task Progress

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/progress_tracker/task_status",
            body=await async_maybe_transform(
                {"job_id": job_id}, task_status_task_status_params.TaskStatusTaskStatusParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskStatusTaskStatusResponse,
        )


class TaskStatusResourceWithRawResponse:
    def __init__(self, task_status: TaskStatusResource) -> None:
        self._task_status = task_status

        self.task_status = to_raw_response_wrapper(
            task_status.task_status,
        )


class AsyncTaskStatusResourceWithRawResponse:
    def __init__(self, task_status: AsyncTaskStatusResource) -> None:
        self._task_status = task_status

        self.task_status = async_to_raw_response_wrapper(
            task_status.task_status,
        )


class TaskStatusResourceWithStreamingResponse:
    def __init__(self, task_status: TaskStatusResource) -> None:
        self._task_status = task_status

        self.task_status = to_streamed_response_wrapper(
            task_status.task_status,
        )


class AsyncTaskStatusResourceWithStreamingResponse:
    def __init__(self, task_status: AsyncTaskStatusResource) -> None:
        self._task_status = task_status

        self.task_status = async_to_streamed_response_wrapper(
            task_status.task_status,
        )
