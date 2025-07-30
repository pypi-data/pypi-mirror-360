# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ExportExportMetadataParams"]


class ExportExportMetadataParams(TypedDict, total=False):
    data_connector_name: Required[str]

    dataslice_id: Optional[str]

    export_file_level: bool

    export_format: Optional[Literal["json", "csv"]]

    selected_metadata_fields: Optional[List[str]]
