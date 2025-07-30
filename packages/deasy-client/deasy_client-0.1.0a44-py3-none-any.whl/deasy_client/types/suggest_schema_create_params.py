# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["SuggestSchemaCreateParams", "Node"]


class SuggestSchemaCreateParams(TypedDict, total=False):
    data_connector_name: Required[str]

    auto_save: Optional[bool]

    condition: Optional["ConditionInputParam"]

    context_level: Optional[str]

    current_tree: Optional[Dict[str, object]]

    dataslice_id: Optional[str]

    deep_suggestion_mode: Optional[bool]

    file_names: Optional[List[str]]

    first_level_clusters: Optional[int]

    graph_tag_type: Optional[Literal["open_ended", "binary", "mixed", "defined_values", "hierarchy"]]

    llm_profile_name: Optional[str]

    max_height: Optional[int]

    max_tags_per_level: Optional[int]

    min_tags_per_level: Optional[int]

    node: Optional[Node]

    not_found_threshold: Optional[float]

    progress_tracking_id: Optional[str]

    schema_name: Optional[str]

    second_level_clusters: Optional[int]

    set_max_values: Optional[bool]

    third_level_clusters: Optional[int]

    use_existing_tags: Optional[bool]

    use_extracted_tags: Optional[bool]

    use_hierarchical_clustering: Optional[bool]

    use_mix_llm_and_source: Optional[bool]

    user_context: Optional[str]

    validate_tags: Optional[bool]

    validation_sample_size: Optional[int]

    values_per_tag: Optional[int]


class Node(TypedDict, total=False):
    label: Optional[str]

    path: Optional[List[str]]


from .condition_input_param import ConditionInputParam
