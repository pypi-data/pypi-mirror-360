# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union
from typing_extensions import TypeAlias

from .._models import BaseModel
from .s3_connector_config import S3ConnectorConfig
from .psql_connector_config import PsqlConnectorConfig
from .qdrant_connector_config import QdrantConnectorConfig
from .sharepoint_connector_config import SharepointConnectorConfig

__all__ = ["ListVdbConnector", "Connectors"]

Connectors: TypeAlias = Union[PsqlConnectorConfig, QdrantConnectorConfig, S3ConnectorConfig, SharepointConnectorConfig]


class ListVdbConnector(BaseModel):
    connectors: Dict[str, Connectors]
