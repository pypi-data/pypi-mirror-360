# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["OpenAIConfig"]


class OpenAIConfig(BaseModel):
    api_key: str

    rpm_completion: int

    tpm_completion: int

    llm_type: Optional[str] = FieldInfo(alias="llmType", default=None)

    rpm_embedding: Optional[int] = None

    temperature: Optional[float] = None

    tpm_embedding: Optional[int] = None
