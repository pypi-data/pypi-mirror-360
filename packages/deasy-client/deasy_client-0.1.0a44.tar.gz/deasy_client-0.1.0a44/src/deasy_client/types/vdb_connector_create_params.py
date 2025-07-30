# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from .s3_connector_config_param import S3ConnectorConfigParam
from .psql_connector_config_param import PsqlConnectorConfigParam
from .qdrant_connector_config_param import QdrantConnectorConfigParam
from .sharepoint_connector_config_param import SharepointConnectorConfigParam

__all__ = ["VdbConnectorCreateParams", "ConnectorBody"]


class VdbConnectorCreateParams(TypedDict, total=False):
    connector_body: Required[ConnectorBody]

    connector_name: Required[str]


ConnectorBody: TypeAlias = Union[
    PsqlConnectorConfigParam, QdrantConnectorConfigParam, S3ConnectorConfigParam, SharepointConnectorConfigParam
]
