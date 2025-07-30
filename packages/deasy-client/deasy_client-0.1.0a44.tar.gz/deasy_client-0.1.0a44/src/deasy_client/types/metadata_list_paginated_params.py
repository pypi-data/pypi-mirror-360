# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, TypedDict

__all__ = ["MetadataListPaginatedParams"]


class MetadataListPaginatedParams(TypedDict, total=False):
    data_connector_name: Required[str]

    conditions: Optional["ConditionInputParam"]

    dataslice_id: Optional[str]

    include_chunk_level: Optional[bool]

    limit: Optional[int]

    offset: Optional[int]

    tag_names: Optional[List[str]]


from .condition_input_param import ConditionInputParam
