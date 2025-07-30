# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, TypedDict

__all__ = ["OcrIngestParams"]


class OcrIngestParams(TypedDict, total=False):
    data_connector_name: Required[str]

    clean_up_out_of_sync: bool

    file_count_to_run: Optional[int]

    file_names: Optional[List[str]]

    job_id: Optional[str]

    llm_profile_name: Optional[str]

    use_llm: bool
