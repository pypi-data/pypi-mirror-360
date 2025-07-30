# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ConditionInputParam", "Tag"]


class Tag(TypedDict, total=False):
    name: Required[str]

    values: Required[List[Union[str, float]]]

    operator: Optional[str]


class ConditionInputParam(TypedDict, total=False):
    children: Optional[Iterable["ConditionInputParam"]]

    condition: Optional[Literal["AND", "OR"]]

    tag: Optional[Tag]
