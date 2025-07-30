# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["TagGetDeleteStatsResponse"]


class TagGetDeleteStatsResponse(BaseModel):
    dataslices_with_tag: List[str]

    file_count_with_tag: int

    graphs_with_tag: List[str]
