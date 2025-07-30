# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["QdrantConnectorConfig", "IndexInfo"]


class IndexInfo(BaseModel):
    total_indexes_found: int


class QdrantConnectorConfig(BaseModel):
    api_key: str

    collection_name: str

    name: str

    url: str

    filename_key: Optional[str] = None

    index_info: Optional[IndexInfo] = None

    text_key: Optional[str] = None

    type: Optional[Literal["QdrantVectorDBManager"]] = None
