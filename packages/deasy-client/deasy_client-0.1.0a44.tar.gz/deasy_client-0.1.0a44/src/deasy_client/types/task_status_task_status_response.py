# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TaskStatusTaskStatusResponse"]


class TaskStatusTaskStatusResponse(BaseModel):
    percent_complete: float

    status: Literal["in_progress", "completed", "aborted", "failed"]
