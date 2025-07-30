# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from .._models import BaseModel

__all__ = ["DatasliceGetMetricsResponse"]


class DatasliceGetMetricsResponse(BaseModel):
    metadata_tag_counts_distribution: Dict[str, List[float]]

    total_file_count: int

    total_metadata_tags: int

    total_node_count: int

    unique_metadata_tags: int
