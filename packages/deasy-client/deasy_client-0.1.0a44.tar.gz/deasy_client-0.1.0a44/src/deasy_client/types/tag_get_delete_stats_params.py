# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TagGetDeleteStatsParams"]


class TagGetDeleteStatsParams(TypedDict, total=False):
    tag_name: Required[str]
