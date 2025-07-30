# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TagCreateParams", "TagData"]


class TagCreateParams(TypedDict, total=False):
    tag_data: Required[TagData]


class TagData(TypedDict, total=False):
    name: Required[str]

    output_type: Required[str]

    available_values: Optional[List[str]]

    date_format: Optional[str]

    description: Optional[str]

    enhance_file_metadata: Optional[bool]

    examples: Optional[List[Union[str, Dict[str, object]]]]

    max_values: Annotated[Optional[int], PropertyInfo(alias="maxValues")]

    tag_id: Optional[str]

    tuned: Optional[int]
