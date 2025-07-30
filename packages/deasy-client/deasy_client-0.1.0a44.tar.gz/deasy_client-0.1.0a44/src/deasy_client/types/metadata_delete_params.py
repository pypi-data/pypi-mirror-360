# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, TypedDict

__all__ = ["MetadataDeleteParams"]


class MetadataDeleteParams(TypedDict, total=False):
    data_connector_name: Required[str]

    conditions: Optional["ConditionInputParam"]

    file_names: Optional[List[str]]

    tags: Optional[List[str]]


from .condition_input_param import ConditionInputParam
