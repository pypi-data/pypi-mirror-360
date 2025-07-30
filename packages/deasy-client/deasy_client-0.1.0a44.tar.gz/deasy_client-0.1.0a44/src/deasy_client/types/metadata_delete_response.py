# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["MetadataDeleteResponse"]


class MetadataDeleteResponse(BaseModel):
    chunk_deleted_count: int

    file_deleted_count: int
