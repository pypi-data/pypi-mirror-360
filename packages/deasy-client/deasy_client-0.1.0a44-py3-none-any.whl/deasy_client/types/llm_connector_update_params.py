# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .openai_config_param import OpenAIConfigParam

__all__ = ["LlmConnectorUpdateParams"]


class LlmConnectorUpdateParams(TypedDict, total=False):
    connector_body: Required[OpenAIConfigParam]

    connector_name: Required[str]
