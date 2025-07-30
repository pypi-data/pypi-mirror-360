# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["S3ConnectorConfigParam"]


class S3ConnectorConfigParam(TypedDict, total=False):
    aws_access_key_id: Required[str]

    aws_secret_access_key: Required[str]

    bucket_name: Required[str]

    name: Required[str]

    type: Literal["S3DataSourceManager"]
