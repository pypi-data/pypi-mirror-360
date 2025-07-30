# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Optional
from typing_extensions import Required, TypedDict

__all__ = [
    "MetadataUpsertParams",
    "MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItem",
    "MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemChunkLevel",
    "MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemFileLevel",
    "MetadataUnionMember1MetadataUnionMember1ItemMetadataUnionMember1MetadataUnionMember1ItemItem",
]


class MetadataUpsertParams(TypedDict, total=False):
    metadata: Required[
        Union[
            Dict[
                str,
                Dict[str, MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItem],
            ],
            Dict[
                str,
                Dict[str, MetadataUnionMember1MetadataUnionMember1ItemMetadataUnionMember1MetadataUnionMember1ItemItem],
            ],
        ]
    ]

    data_connector_name: Optional[str]

    dataslice_id: Optional[str]


class MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemChunkLevel(
    TypedDict, total=False
):
    values: Required[List[Union[str, float]]]

    evidence: Optional[str]


class MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemFileLevel(
    TypedDict, total=False
):
    values: Required[List[Union[str, float]]]

    evidence: Optional[str]


class MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItem(
    TypedDict, total=False
):
    chunk_level: Optional[
        Dict[
            str,
            Optional[
                MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemChunkLevel
            ],
        ]
    ]

    file_level: Optional[
        MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemFileLevel
    ]


class MetadataUnionMember1MetadataUnionMember1ItemMetadataUnionMember1MetadataUnionMember1ItemItem(
    TypedDict, total=False
):
    values: Required[List[Union[str, float]]]

    evidence: Optional[str]
