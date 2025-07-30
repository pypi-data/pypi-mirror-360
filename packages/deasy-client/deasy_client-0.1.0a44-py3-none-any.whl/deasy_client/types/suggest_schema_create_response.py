# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SuggestSchemaCreateResponse", "Node", "SuggestedTags"]


class Node(BaseModel):
    label: Optional[str] = None

    path: Optional[List[str]] = None


class SuggestedTags(BaseModel):
    name: str

    output_type: str

    available_values: Optional[List[str]] = None

    date_format: Optional[str] = None

    description: Optional[str] = None

    enhance_file_metadata: Optional[bool] = None

    examples: Optional[List[Union[str, Dict[str, object]]]] = None

    max_values: Optional[int] = FieldInfo(alias="maxValues", default=None)

    tag_id: Optional[str] = None

    tuned: Optional[int] = None


class SuggestSchemaCreateResponse(BaseModel):
    suggestion: Dict[str, object]

    message: Optional[str] = None

    node: Optional[Node] = None

    status_code: Optional[int] = None

    suggested_tags: Optional[Dict[str, SuggestedTags]] = None

    tag_not_found_rates: Optional[Dict[str, float]] = None
