# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .openai_config import OpenAIConfig

__all__ = ["LlmConnectorListResponse", "Connectors", "ConnectorsDeasyComputeConfig"]


class ConnectorsDeasyComputeConfig(BaseModel):
    llm_type: Optional[str] = FieldInfo(alias="llmType", default=None)


Connectors: TypeAlias = Union[ConnectorsDeasyComputeConfig, OpenAIConfig]


class LlmConnectorListResponse(BaseModel):
    connectors: Dict[str, Connectors]
