# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.dataslice import export_export_metadata_params

__all__ = ["ExportResource", "AsyncExportResource"]


class ExportResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return ExportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return ExportResourceWithStreamingResponse(self)

    def export_metadata(
        self,
        *,
        data_connector_name: str,
        dataslice_id: Optional[str] | NotGiven = NOT_GIVEN,
        export_file_level: bool | NotGiven = NOT_GIVEN,
        export_format: Optional[Literal["json", "csv"]] | NotGiven = NOT_GIVEN,
        selected_metadata_fields: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Export file-level/chunk-level metadata for a use case

        Attributes:

            data_connector_name: The name of the vdb profile to export metadata from.
            dataslice_id: The id of the dataslice to export metadata from.
            export_file_level: Whether to export file-level metadata or chunk-level metadata.
            export_format: The format to export the metadata in, JSON or CSV.
            selected_metadata_fields: The metadata fields to include in the export.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/dataslice/export/metadata",
            body=maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "dataslice_id": dataslice_id,
                    "export_file_level": export_file_level,
                    "export_format": export_format,
                    "selected_metadata_fields": selected_metadata_fields,
                },
                export_export_metadata_params.ExportExportMetadataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncExportResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#accessing-raw-response-data-eg-headers
        """
        return AsyncExportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Deasie-internal/deasy-labs#with_streaming_response
        """
        return AsyncExportResourceWithStreamingResponse(self)

    async def export_metadata(
        self,
        *,
        data_connector_name: str,
        dataslice_id: Optional[str] | NotGiven = NOT_GIVEN,
        export_file_level: bool | NotGiven = NOT_GIVEN,
        export_format: Optional[Literal["json", "csv"]] | NotGiven = NOT_GIVEN,
        selected_metadata_fields: Optional[List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Export file-level/chunk-level metadata for a use case

        Attributes:

            data_connector_name: The name of the vdb profile to export metadata from.
            dataslice_id: The id of the dataslice to export metadata from.
            export_file_level: Whether to export file-level metadata or chunk-level metadata.
            export_format: The format to export the metadata in, JSON or CSV.
            selected_metadata_fields: The metadata fields to include in the export.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/dataslice/export/metadata",
            body=await async_maybe_transform(
                {
                    "data_connector_name": data_connector_name,
                    "dataslice_id": dataslice_id,
                    "export_file_level": export_file_level,
                    "export_format": export_format,
                    "selected_metadata_fields": selected_metadata_fields,
                },
                export_export_metadata_params.ExportExportMetadataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ExportResourceWithRawResponse:
    def __init__(self, export: ExportResource) -> None:
        self._export = export

        self.export_metadata = to_raw_response_wrapper(
            export.export_metadata,
        )


class AsyncExportResourceWithRawResponse:
    def __init__(self, export: AsyncExportResource) -> None:
        self._export = export

        self.export_metadata = async_to_raw_response_wrapper(
            export.export_metadata,
        )


class ExportResourceWithStreamingResponse:
    def __init__(self, export: ExportResource) -> None:
        self._export = export

        self.export_metadata = to_streamed_response_wrapper(
            export.export_metadata,
        )


class AsyncExportResourceWithStreamingResponse:
    def __init__(self, export: AsyncExportResource) -> None:
        self._export = export

        self.export_metadata = async_to_streamed_response_wrapper(
            export.export_metadata,
        )
