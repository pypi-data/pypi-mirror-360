# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["OpenAIConfigParam"]


class OpenAIConfigParam(TypedDict, total=False):
    api_key: Required[str]

    rpm_completion: Required[int]

    tpm_completion: Required[int]

    llm_type: Annotated[str, PropertyInfo(alias="llmType")]

    rpm_embedding: Optional[int]

    temperature: float

    tpm_embedding: Optional[int]
