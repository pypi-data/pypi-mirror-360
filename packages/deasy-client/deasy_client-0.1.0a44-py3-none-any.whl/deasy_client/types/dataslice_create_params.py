# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["DatasliceCreateParams"]


class DatasliceCreateParams(TypedDict, total=False):
    data_connector_name: Required[str]

    dataslice_name: Required[str]

    graph_id: Required[str]

    latest_graph: Required[Dict[str, object]]

    condition: Optional["ConditionInputParam"]

    data_points: Optional[int]

    description: Optional[str]

    parent_dataslice_id: Optional[str]

    status: str


from .condition_input_param import ConditionInputParam
