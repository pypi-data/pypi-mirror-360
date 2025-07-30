# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, TypedDict

__all__ = ["SuggestDescriptionCreateParams"]


class SuggestDescriptionCreateParams(TypedDict, total=False):
    data_connector_name: Required[str]

    tag_name: Required[str]

    available_values: Optional[List[str]]

    context: Optional[str]

    current_description: Optional[str]

    dataslice_id: Optional[str]

    llm_profile_name: Optional[str]
