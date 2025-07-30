# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List
from datetime import datetime

from .._models import BaseModel

__all__ = ["SchemaListResponse", "Schema"]


class Schema(BaseModel):
    created_at: datetime

    schema_data: Dict[str, object]

    schema_description: str

    schema_id: str

    schema_name: str

    updated_at: datetime

    user_id: str


class SchemaListResponse(BaseModel):
    schemas: List[Schema]
