# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import TypedDict

__all__ = ["SchemaListParams"]


class SchemaListParams(TypedDict, total=False):
    schema_ids: Optional[List[str]]
