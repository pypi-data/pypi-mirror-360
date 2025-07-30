# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["DatasliceGetFileCountParams"]


class DatasliceGetFileCountParams(TypedDict, total=False):
    data_connector_name: Required[str]

    condition: Optional["ConditionInputParam"]

    dataslice_id: Optional[str]


from .condition_input_param import ConditionInputParam
