# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DeasySelectQueryParams", "TagDistributions", "TagDistributionsValues", "TagSchema"]


class DeasySelectQueryParams(TypedDict, total=False):
    data_connector_name: Required[str]

    query: Required[str]

    banned_filters: Optional[Dict[str, List[Union[str, float]]]]

    file_hybrid_search_boost: Optional[float]

    metadata_hybrid_search: Optional[bool]

    metadata_hybrid_search_boost: Optional[float]

    metadata_reranker: Optional[bool]

    return_only_query: Optional[bool]

    tag_distributions: Optional[Dict[str, TagDistributions]]

    tag_level: Optional[Literal["chunk", "both"]]

    tag_names: Optional[List[str]]

    tag_schemas: Optional[Iterable[TagSchema]]

    top_k: Optional[int]

    with_text: Optional[bool]


class TagDistributionsValues(TypedDict, total=False):
    file_count: Required[int]

    chunk_count: Optional[int]

    percentage: Optional[float]


class TagDistributions(TypedDict, total=False):
    values: Required[Dict[str, TagDistributionsValues]]

    coverage_percentage: Optional[float]

    total_count: Optional[int]


class TagSchema(TypedDict, total=False):
    description: Required[str]

    name: Required[str]

    available_values: Optional[List[Union[str, float]]]

    created_at: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    date_format: Optional[str]

    enhance_file_metadata: Optional[bool]

    examples: Optional[List[Union[str, Dict[str, object]]]]

    max_values: Annotated[Union[int, str, Iterable[object], None], PropertyInfo(alias="maxValues")]

    neg_examples: Optional[List[str]]

    output_type: Optional[str]

    retry_feedback: Optional[Dict[str, object]]

    strategy: Optional[str]

    tag_id: Optional[str]

    truncated_available_values: Optional[bool]

    tuned: Optional[int]

    updated_at: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    username: Optional[str]
