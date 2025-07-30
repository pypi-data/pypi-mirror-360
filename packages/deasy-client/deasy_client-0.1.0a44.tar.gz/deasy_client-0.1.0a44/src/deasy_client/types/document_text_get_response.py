# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict

from .._models import BaseModel

__all__ = ["DocumentTextGetResponse"]


class DocumentTextGetResponse(BaseModel):
    file_to_nodes_to_text: Dict[str, Dict[str, str]]
