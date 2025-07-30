# DeasySelect

Methods:

- <code title="post /deasy_select/query">client.deasy_select.<a href="./src/deasy_client/resources/deasy_select.py">query</a>(\*\*<a href="src/deasy_client/types/deasy_select_query_params.py">params</a>) -> object</code>

# ClassifyBulk

Types:

```python
from deasy_client.types import ConditionInput, ClassifyBulkClassifyResponse
```

Methods:

- <code title="post /classify_bulk">client.classify_bulk.<a href="./src/deasy_client/resources/classify_bulk.py">classify</a>(\*\*<a href="src/deasy_client/types/classify_bulk_classify_params.py">params</a>) -> <a href="./src/deasy_client/types/classify_bulk_classify_response.py">ClassifyBulkClassifyResponse</a></code>

# Classify

Types:

```python
from deasy_client.types import ClassifyClassifyFilesResponse
```

Methods:

- <code title="post /classify">client.classify.<a href="./src/deasy_client/resources/classify.py">classify_files</a>(\*\*<a href="src/deasy_client/types/classify_classify_files_params.py">params</a>) -> <a href="./src/deasy_client/types/classify_classify_files_response.py">ClassifyClassifyFilesResponse</a></code>

# PrepareData

Types:

```python
from deasy_client.types import PrepareDataCreateResponse
```

Methods:

- <code title="post /prepare_data">client.prepare_data.<a href="./src/deasy_client/resources/prepare_data.py">create</a>(\*\*<a href="src/deasy_client/types/prepare_data_create_params.py">params</a>) -> <a href="./src/deasy_client/types/prepare_data_create_response.py">PrepareDataCreateResponse</a></code>

# SuggestSchema

Types:

```python
from deasy_client.types import SuggestSchemaCreateResponse
```

Methods:

- <code title="post /suggest_schema">client.suggest_schema.<a href="./src/deasy_client/resources/suggest_schema.py">create</a>(\*\*<a href="src/deasy_client/types/suggest_schema_create_params.py">params</a>) -> <a href="./src/deasy_client/types/suggest_schema_create_response.py">SuggestSchemaCreateResponse</a></code>

# SuggestDescription

Types:

```python
from deasy_client.types import SuggestDescriptionCreateResponse
```

Methods:

- <code title="post /suggest_description">client.suggest_description.<a href="./src/deasy_client/resources/suggest_description.py">create</a>(\*\*<a href="src/deasy_client/types/suggest_description_create_params.py">params</a>) -> <a href="./src/deasy_client/types/suggest_description_create_response.py">SuggestDescriptionCreateResponse</a></code>

# Ocr

Methods:

- <code title="post /ocr/ingest">client.ocr.<a href="./src/deasy_client/resources/ocr.py">ingest</a>(\*\*<a href="src/deasy_client/types/ocr_ingest_params.py">params</a>) -> object</code>

# TaskStatus

Types:

```python
from deasy_client.types import TaskStatusTaskStatusResponse
```

Methods:

- <code title="post /progress_tracker/task_status">client.task_status.<a href="./src/deasy_client/resources/task_status.py">task_status</a>(\*\*<a href="src/deasy_client/types/task_status_task_status_params.py">params</a>) -> <a href="./src/deasy_client/types/task_status_task_status_response.py">TaskStatusTaskStatusResponse</a></code>

# DocumentText

Types:

```python
from deasy_client.types import DocumentTextGetResponse
```

Methods:

- <code title="post /data/document_text">client.document_text.<a href="./src/deasy_client/resources/document_text.py">get</a>(\*\*<a href="src/deasy_client/types/document_text_get_params.py">params</a>) -> <a href="./src/deasy_client/types/document_text_get_response.py">DocumentTextGetResponse</a></code>

# Tags

Types:

```python
from deasy_client.types import (
    DeasyTag,
    TagResponse,
    TagCreateResponse,
    TagListResponse,
    TagGetDeleteStatsResponse,
    TagUpsertResponse,
)
```

Methods:

- <code title="post /tags/create">client.tags.<a href="./src/deasy_client/resources/tags.py">create</a>(\*\*<a href="src/deasy_client/types/tag_create_params.py">params</a>) -> <a href="./src/deasy_client/types/tag_create_response.py">TagCreateResponse</a></code>
- <code title="put /tags/update">client.tags.<a href="./src/deasy_client/resources/tags.py">update</a>(\*\*<a href="src/deasy_client/types/tag_update_params.py">params</a>) -> <a href="./src/deasy_client/types/tag_response.py">TagResponse</a></code>
- <code title="get /tags/list">client.tags.<a href="./src/deasy_client/resources/tags.py">list</a>() -> <a href="./src/deasy_client/types/tag_list_response.py">TagListResponse</a></code>
- <code title="delete /tags/delete">client.tags.<a href="./src/deasy_client/resources/tags.py">delete</a>(\*\*<a href="src/deasy_client/types/tag_delete_params.py">params</a>) -> <a href="./src/deasy_client/types/tag_response.py">TagResponse</a></code>
- <code title="post /tags/delete_stats">client.tags.<a href="./src/deasy_client/resources/tags.py">get_delete_stats</a>(\*\*<a href="src/deasy_client/types/tag_get_delete_stats_params.py">params</a>) -> <a href="./src/deasy_client/types/tag_get_delete_stats_response.py">TagGetDeleteStatsResponse</a></code>
- <code title="post /tags/upsert">client.tags.<a href="./src/deasy_client/resources/tags.py">upsert</a>(\*\*<a href="src/deasy_client/types/tag_upsert_params.py">params</a>) -> <a href="./src/deasy_client/types/tag_upsert_response.py">TagUpsertResponse</a></code>

# Metadata

Types:

```python
from deasy_client.types import (
    MetadataListResponse,
    MetadataDeleteResponse,
    MetadataGetDistributionsResponse,
    MetadataListPaginatedResponse,
    MetadataUpsertResponse,
)
```

Methods:

- <code title="post /metadata/list">client.metadata.<a href="./src/deasy_client/resources/metadata.py">list</a>(\*\*<a href="src/deasy_client/types/metadata_list_params.py">params</a>) -> <a href="./src/deasy_client/types/metadata_list_response.py">MetadataListResponse</a></code>
- <code title="post /metadata/delete">client.metadata.<a href="./src/deasy_client/resources/metadata.py">delete</a>(\*\*<a href="src/deasy_client/types/metadata_delete_params.py">params</a>) -> <a href="./src/deasy_client/types/metadata_delete_response.py">MetadataDeleteResponse</a></code>
- <code title="post /metadata/get_distributions">client.metadata.<a href="./src/deasy_client/resources/metadata.py">get_distributions</a>(\*\*<a href="src/deasy_client/types/metadata_get_distributions_params.py">params</a>) -> <a href="./src/deasy_client/types/metadata_get_distributions_response.py">MetadataGetDistributionsResponse</a></code>
- <code title="post /metadata/list_paginated">client.metadata.<a href="./src/deasy_client/resources/metadata.py">list_paginated</a>(\*\*<a href="src/deasy_client/types/metadata_list_paginated_params.py">params</a>) -> <a href="./src/deasy_client/types/metadata_list_paginated_response.py">MetadataListPaginatedResponse</a></code>
- <code title="post /metadata/upsert">client.metadata.<a href="./src/deasy_client/resources/metadata.py">upsert</a>(\*\*<a href="src/deasy_client/types/metadata_upsert_params.py">params</a>) -> <a href="./src/deasy_client/types/metadata_upsert_response.py">MetadataUpsertResponse</a></code>

# VdbConnector

Types:

```python
from deasy_client.types import (
    ConnectorResponse,
    DeleteConnector,
    ListVdbConnector,
    PsqlConnectorConfig,
    QdrantConnectorConfig,
    S3ConnectorConfig,
    SharepointConnectorConfig,
    VdbConnectorGetDeleteStatsResponse,
)
```

Methods:

- <code title="post /vdb_connector/create">client.vdb_connector.<a href="./src/deasy_client/resources/vdb_connector.py">create</a>(\*\*<a href="src/deasy_client/types/vdb_connector_create_params.py">params</a>) -> <a href="./src/deasy_client/types/connector_response.py">ConnectorResponse</a></code>
- <code title="post /vdb_connector/update">client.vdb_connector.<a href="./src/deasy_client/resources/vdb_connector.py">update</a>(\*\*<a href="src/deasy_client/types/vdb_connector_update_params.py">params</a>) -> <a href="./src/deasy_client/types/connector_response.py">ConnectorResponse</a></code>
- <code title="post /vdb_connector/list">client.vdb_connector.<a href="./src/deasy_client/resources/vdb_connector.py">list</a>() -> <a href="./src/deasy_client/types/list_vdb_connector.py">ListVdbConnector</a></code>
- <code title="post /vdb_connector/delete">client.vdb_connector.<a href="./src/deasy_client/resources/vdb_connector.py">delete</a>(\*\*<a href="src/deasy_client/types/vdb_connector_delete_params.py">params</a>) -> <a href="./src/deasy_client/types/connector_response.py">ConnectorResponse</a></code>
- <code title="post /vdb_connector/delete_stats">client.vdb_connector.<a href="./src/deasy_client/resources/vdb_connector.py">get_delete_stats</a>(\*\*<a href="src/deasy_client/types/vdb_connector_get_delete_stats_params.py">params</a>) -> <a href="./src/deasy_client/types/vdb_connector_get_delete_stats_response.py">VdbConnectorGetDeleteStatsResponse</a></code>

# LlmConnector

Types:

```python
from deasy_client.types import OpenAIConfig, LlmConnectorListResponse
```

Methods:

- <code title="post /llm_connector/create">client.llm_connector.<a href="./src/deasy_client/resources/llm_connector.py">create</a>(\*\*<a href="src/deasy_client/types/llm_connector_create_params.py">params</a>) -> <a href="./src/deasy_client/types/connector_response.py">ConnectorResponse</a></code>
- <code title="post /llm_connector/update">client.llm_connector.<a href="./src/deasy_client/resources/llm_connector.py">update</a>(\*\*<a href="src/deasy_client/types/llm_connector_update_params.py">params</a>) -> <a href="./src/deasy_client/types/connector_response.py">ConnectorResponse</a></code>
- <code title="post /llm_connector/list">client.llm_connector.<a href="./src/deasy_client/resources/llm_connector.py">list</a>() -> <a href="./src/deasy_client/types/llm_connector_list_response.py">LlmConnectorListResponse</a></code>
- <code title="post /llm_connector/delete">client.llm_connector.<a href="./src/deasy_client/resources/llm_connector.py">delete</a>(\*\*<a href="src/deasy_client/types/llm_connector_delete_params.py">params</a>) -> <a href="./src/deasy_client/types/connector_response.py">ConnectorResponse</a></code>

# Dataslice

Types:

```python
from deasy_client.types import (
    ConditionOutput,
    DatasliceCreateResponse,
    DatasliceListResponse,
    DatasliceDeleteResponse,
    DatasliceGetFileCountResponse,
    DatasliceGetFilesResponse,
    DatasliceGetMetricsResponse,
    DatasliceGetTagVdbDistributionResponse,
)
```

Methods:

- <code title="post /dataslice/create">client.dataslice.<a href="./src/deasy_client/resources/dataslice/dataslice.py">create</a>(\*\*<a href="src/deasy_client/types/dataslice_create_params.py">params</a>) -> <a href="./src/deasy_client/types/dataslice_create_response.py">DatasliceCreateResponse</a></code>
- <code title="get /dataslice/list">client.dataslice.<a href="./src/deasy_client/resources/dataslice/dataslice.py">list</a>() -> <a href="./src/deasy_client/types/dataslice_list_response.py">DatasliceListResponse</a></code>
- <code title="delete /dataslice/delete">client.dataslice.<a href="./src/deasy_client/resources/dataslice/dataslice.py">delete</a>(\*\*<a href="src/deasy_client/types/dataslice_delete_params.py">params</a>) -> <a href="./src/deasy_client/types/dataslice_delete_response.py">DatasliceDeleteResponse</a></code>
- <code title="post /dataslice/file_count">client.dataslice.<a href="./src/deasy_client/resources/dataslice/dataslice.py">get_file_count</a>(\*\*<a href="src/deasy_client/types/dataslice_get_file_count_params.py">params</a>) -> <a href="./src/deasy_client/types/dataslice_get_file_count_response.py">DatasliceGetFileCountResponse</a></code>
- <code title="post /dataslice/files">client.dataslice.<a href="./src/deasy_client/resources/dataslice/dataslice.py">get_files</a>(\*\*<a href="src/deasy_client/types/dataslice_get_files_params.py">params</a>) -> <a href="./src/deasy_client/types/dataslice_get_files_response.py">DatasliceGetFilesResponse</a></code>
- <code title="post /dataslice/metrics">client.dataslice.<a href="./src/deasy_client/resources/dataslice/dataslice.py">get_metrics</a>(\*\*<a href="src/deasy_client/types/dataslice_get_metrics_params.py">params</a>) -> <a href="./src/deasy_client/types/dataslice_get_metrics_response.py">DatasliceGetMetricsResponse</a></code>
- <code title="post /dataslice/tag_vdb_distribution">client.dataslice.<a href="./src/deasy_client/resources/dataslice/dataslice.py">get_tag_vdb_distribution</a>(\*\*<a href="src/deasy_client/types/dataslice_get_tag_vdb_distribution_params.py">params</a>) -> <a href="./src/deasy_client/types/dataslice_get_tag_vdb_distribution_response.py">DatasliceGetTagVdbDistributionResponse</a></code>

## Export

Methods:

- <code title="post /dataslice/export/metadata">client.dataslice.export.<a href="./src/deasy_client/resources/dataslice/export.py">export_metadata</a>(\*\*<a href="src/deasy_client/types/dataslice/export_export_metadata_params.py">params</a>) -> object</code>

# Schema

Types:

```python
from deasy_client.types import SchemaOperationResponse, SchemaListResponse
```

Methods:

- <code title="post /schema/create">client.schema.<a href="./src/deasy_client/resources/schema.py">create</a>(\*\*<a href="src/deasy_client/types/schema_create_params.py">params</a>) -> <a href="./src/deasy_client/types/schema_operation_response.py">SchemaOperationResponse</a></code>
- <code title="post /schema/update">client.schema.<a href="./src/deasy_client/resources/schema.py">update</a>(\*\*<a href="src/deasy_client/types/schema_update_params.py">params</a>) -> <a href="./src/deasy_client/types/schema_operation_response.py">SchemaOperationResponse</a></code>
- <code title="post /schema/list">client.schema.<a href="./src/deasy_client/resources/schema.py">list</a>(\*\*<a href="src/deasy_client/types/schema_list_params.py">params</a>) -> <a href="./src/deasy_client/types/schema_list_response.py">SchemaListResponse</a></code>
- <code title="delete /schema/delete">client.schema.<a href="./src/deasy_client/resources/schema.py">delete</a>(\*\*<a href="src/deasy_client/types/schema_delete_params.py">params</a>) -> <a href="./src/deasy_client/types/schema_operation_response.py">SchemaOperationResponse</a></code>
- <code title="post /schema/upsert">client.schema.<a href="./src/deasy_client/resources/schema.py">upsert</a>(\*\*<a href="src/deasy_client/types/schema_upsert_params.py">params</a>) -> <a href="./src/deasy_client/types/schema_operation_response.py">SchemaOperationResponse</a></code>
