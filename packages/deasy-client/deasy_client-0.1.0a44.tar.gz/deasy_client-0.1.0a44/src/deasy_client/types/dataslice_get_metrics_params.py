# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import TypedDict

__all__ = ["DatasliceGetMetricsParams"]


class DatasliceGetMetricsParams(TypedDict, total=False):
    data_connector_name: Optional[str]

    dataslice_id: Optional[str]

    file_names: Optional[List[str]]

    node_ids: Optional[List[str]]

    tags: Optional[List[str]]
