# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, TypedDict

__all__ = ["DocumentTextGetParams"]


class DocumentTextGetParams(TypedDict, total=False):
    data_connector_name: Required[str]

    file_names: Required[List[str]]

    chunk_ids: Optional[List[str]]
