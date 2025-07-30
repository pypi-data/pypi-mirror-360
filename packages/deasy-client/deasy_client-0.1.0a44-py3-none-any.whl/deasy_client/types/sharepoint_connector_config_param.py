# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SharepointConnectorConfigParam"]


class SharepointConnectorConfigParam(TypedDict, total=False):
    client_id: Required[str]

    client_secret: Required[str]

    name: Required[str]

    sharepoint_site_name: Required[str]

    tenant_id: Required[str]

    type: Literal["SharepointDataSourceManager"]
