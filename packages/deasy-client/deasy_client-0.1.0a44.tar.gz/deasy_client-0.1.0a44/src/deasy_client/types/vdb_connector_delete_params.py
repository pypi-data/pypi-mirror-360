# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["VdbConnectorDeleteParams"]


class VdbConnectorDeleteParams(TypedDict, total=False):
    connector_name: Required[str]
