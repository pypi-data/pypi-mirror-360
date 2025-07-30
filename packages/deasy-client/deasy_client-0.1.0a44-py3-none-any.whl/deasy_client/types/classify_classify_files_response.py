# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict

from .._models import BaseModel

__all__ = ["ClassifyClassifyFilesResponse"]


class ClassifyClassifyFilesResponse(BaseModel):
    message: str

    output: Dict[str, object]
