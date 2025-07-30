# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["SharepointConnectorConfig"]


class SharepointConnectorConfig(BaseModel):
    client_id: str

    client_secret: str

    name: str

    sharepoint_site_name: str

    tenant_id: str

    type: Optional[Literal["SharepointDataSourceManager"]] = None
