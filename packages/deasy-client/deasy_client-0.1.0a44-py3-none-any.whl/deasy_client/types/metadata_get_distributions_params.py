# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, TypedDict

__all__ = ["MetadataGetDistributionsParams"]


class MetadataGetDistributionsParams(TypedDict, total=False):
    data_connector_name: Required[str]

    dataslice_id: Optional[str]

    schema_name: Optional[str]

    tag_names: Optional[List[str]]
