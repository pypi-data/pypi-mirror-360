# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .deasy_tag import DeasyTag

__all__ = ["TagListResponse"]


class TagListResponse(BaseModel):
    tags: List[DeasyTag]
