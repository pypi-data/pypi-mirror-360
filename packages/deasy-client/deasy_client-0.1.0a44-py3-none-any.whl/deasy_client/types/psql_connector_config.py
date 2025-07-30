# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["PsqlConnectorConfig", "IndexInfo"]


class IndexInfo(BaseModel):
    found_indexes: List[str]

    total_indexes_found: int


class PsqlConnectorConfig(BaseModel):
    collection_name: str

    database_name: str

    db_user: str

    name: str

    password: str

    port: str

    url: str

    filename_key: Optional[str] = None

    index_info: Optional[IndexInfo] = None

    text_key: Optional[str] = None

    type: Optional[Literal["PSQLVectorDBManager"]] = None
