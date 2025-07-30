# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional

from .._models import BaseModel

__all__ = [
    "MetadataListResponse",
    "MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItem",
    "MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemChunkLevel",
    "MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemFileLevel",
    "MetadataUnionMember1MetadataUnionMember1ItemMetadataUnionMember1MetadataUnionMember1ItemItem",
]


class MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemChunkLevel(BaseModel):
    values: List[Union[str, float]]

    evidence: Optional[str] = None


class MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemFileLevel(BaseModel):
    values: List[Union[str, float]]

    evidence: Optional[str] = None


class MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItem(BaseModel):
    chunk_level: Optional[
        Dict[
            str,
            Optional[
                MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemChunkLevel
            ],
        ]
    ] = None

    file_level: Optional[
        MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItemFileLevel
    ] = None


class MetadataUnionMember1MetadataUnionMember1ItemMetadataUnionMember1MetadataUnionMember1ItemItem(BaseModel):
    values: List[Union[str, float]]

    evidence: Optional[str] = None


class MetadataListResponse(BaseModel):
    metadata: Union[
        Dict[
            str, Dict[str, MetadataUnionMember0MetadataUnionMember0ItemMetadataUnionMember0MetadataUnionMember0ItemItem]
        ],
        Dict[
            str, Dict[str, MetadataUnionMember1MetadataUnionMember1ItemMetadataUnionMember1MetadataUnionMember1ItemItem]
        ],
    ]
