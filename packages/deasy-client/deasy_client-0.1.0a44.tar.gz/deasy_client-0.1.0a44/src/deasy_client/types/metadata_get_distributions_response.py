# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["MetadataGetDistributionsResponse", "TagsSchema"]


class TagsSchema(BaseModel):
    description: str

    name: str

    available_values: Optional[List[Union[str, float]]] = None

    created_at: Optional[datetime] = None

    date_format: Optional[str] = None

    enhance_file_metadata: Optional[bool] = None

    examples: Optional[List[Union[str, Dict[str, object]]]] = None

    max_values: Union[int, str, List[object], None] = FieldInfo(alias="maxValues", default=None)

    neg_examples: Optional[List[str]] = None

    output_type: Optional[str] = None

    retry_feedback: Optional[Dict[str, object]] = None

    strategy: Optional[str] = None

    tag_id: Optional[str] = None

    truncated_available_values: Optional[bool] = None

    tuned: Optional[int] = None

    updated_at: Optional[datetime] = None

    username: Optional[str] = None


class MetadataGetDistributionsResponse(BaseModel):
    count_distribution: Dict[str, Dict[str, object]]

    tags_schemas: List[TagsSchema]
