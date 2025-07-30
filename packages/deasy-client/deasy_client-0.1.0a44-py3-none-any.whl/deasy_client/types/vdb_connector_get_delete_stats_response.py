# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["VdbConnectorGetDeleteStatsResponse"]


class VdbConnectorGetDeleteStatsResponse(BaseModel):
    dataslices_for_vdb: List[str]

    file_count_with_vdb: int
