# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["S3ConnectorConfig"]


class S3ConnectorConfig(BaseModel):
    aws_access_key_id: str

    aws_secret_access_key: str

    bucket_name: str

    name: str

    type: Optional[Literal["S3DataSourceManager"]] = None
