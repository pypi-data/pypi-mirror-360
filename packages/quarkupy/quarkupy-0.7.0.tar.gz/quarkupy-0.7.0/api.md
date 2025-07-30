# Quark

Methods:

- <code title="get /">client.<a href="./src/quarkupy/_client.py">retrieve</a>() -> object</code>

# Context

## Extractors

Types:

```python
from quarkupy.types.context import (
    Extractor,
    ReferenceDepth,
    SuccessResponseMessage,
    ExtractorListResponse,
)
```

Methods:

- <code title="get /context/extractors/{id}">client.context.extractors.<a href="./src/quarkupy/resources/context/extractors.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/context/extractor.py">Extractor</a></code>
- <code title="put /context/extractors">client.context.extractors.<a href="./src/quarkupy/resources/context/extractors.py">update</a>(\*\*<a href="src/quarkupy/types/context/extractor_update_params.py">params</a>) -> <a href="./src/quarkupy/types/context/extractor.py">Extractor</a></code>
- <code title="get /context/extractors">client.context.extractors.<a href="./src/quarkupy/resources/context/extractors.py">list</a>() -> <a href="./src/quarkupy/types/context/extractor_list_response.py">ExtractorListResponse</a></code>
- <code title="delete /context/extractors/{id}">client.context.extractors.<a href="./src/quarkupy/resources/context/extractors.py">delete</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /context/extractors/schema">client.context.extractors.<a href="./src/quarkupy/resources/context/extractors.py">retrieve_schema</a>() -> object</code>
- <code title="patch /context/extractors/{id}">client.context.extractors.<a href="./src/quarkupy/resources/context/extractors.py">update_partial</a>(id, \*\*<a href="src/quarkupy/types/context/extractor_update_partial_params.py">params</a>) -> <a href="./src/quarkupy/types/context/extractor.py">Extractor</a></code>

## Classifiers

Types:

```python
from quarkupy.types.context import Classifier, ClassifierListResponse
```

Methods:

- <code title="get /context/classifiers/{id}">client.context.classifiers.<a href="./src/quarkupy/resources/context/classifiers.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/context/classifier.py">Classifier</a></code>
- <code title="put /context/classifiers">client.context.classifiers.<a href="./src/quarkupy/resources/context/classifiers.py">update</a>(\*\*<a href="src/quarkupy/types/context/classifier_update_params.py">params</a>) -> <a href="./src/quarkupy/types/context/classifier.py">Classifier</a></code>
- <code title="get /context/classifiers">client.context.classifiers.<a href="./src/quarkupy/resources/context/classifiers.py">list</a>() -> <a href="./src/quarkupy/types/context/classifier_list_response.py">ClassifierListResponse</a></code>
- <code title="delete /context/classifiers/{id}">client.context.classifiers.<a href="./src/quarkupy/resources/context/classifiers.py">delete</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /context/classifiers/schema">client.context.classifiers.<a href="./src/quarkupy/resources/context/classifiers.py">retrieve_schema</a>() -> object</code>
- <code title="patch /context/classifiers/{id}">client.context.classifiers.<a href="./src/quarkupy/resources/context/classifiers.py">update_partial</a>(id, \*\*<a href="src/quarkupy/types/context/classifier_update_partial_params.py">params</a>) -> <a href="./src/quarkupy/types/context/classifier.py">Classifier</a></code>

# Admin

## Identity

### Identity

Types:

```python
from quarkupy.types.admin.identity import IdentityModel, IdentityListResponse
```

Methods:

- <code title="get /admin/identity/identity/{id}">client.admin.identity.identity.<a href="./src/quarkupy/resources/admin/identity/identity_.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/admin/identity/identity_model.py">IdentityModel</a></code>
- <code title="patch /admin/identity/identity/{id}">client.admin.identity.identity.<a href="./src/quarkupy/resources/admin/identity/identity_.py">update</a>(id, \*\*<a href="src/quarkupy/types/admin/identity/identity_update_params.py">params</a>) -> <a href="./src/quarkupy/types/admin/identity/identity_model.py">IdentityModel</a></code>
- <code title="get /admin/identity/identity">client.admin.identity.identity.<a href="./src/quarkupy/resources/admin/identity/identity_.py">list</a>() -> <a href="./src/quarkupy/types/admin/identity/identity_list_response.py">IdentityListResponse</a></code>
- <code title="delete /admin/identity/identity/{id}">client.admin.identity.identity.<a href="./src/quarkupy/resources/admin/identity/identity_.py">delete</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>

### Roles

Types:

```python
from quarkupy.types.admin.identity import IdentityRole, Role, RoleListResponse
```

Methods:

- <code title="put /admin/identity/roles">client.admin.identity.roles.<a href="./src/quarkupy/resources/admin/identity/roles/roles.py">create</a>(\*\*<a href="src/quarkupy/types/admin/identity/role_create_params.py">params</a>) -> <a href="./src/quarkupy/types/admin/identity/identity_role.py">IdentityRole</a></code>
- <code title="get /admin/identity/roles/{id}">client.admin.identity.roles.<a href="./src/quarkupy/resources/admin/identity/roles/roles.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/admin/identity/identity_role.py">IdentityRole</a></code>
- <code title="patch /admin/identity/roles/{id}">client.admin.identity.roles.<a href="./src/quarkupy/resources/admin/identity/roles/roles.py">update</a>(id, \*\*<a href="src/quarkupy/types/admin/identity/role_update_params.py">params</a>) -> <a href="./src/quarkupy/types/admin/identity/identity_role.py">IdentityRole</a></code>
- <code title="get /admin/identity/roles">client.admin.identity.roles.<a href="./src/quarkupy/resources/admin/identity/roles/roles.py">list</a>() -> <a href="./src/quarkupy/types/admin/identity/role_list_response.py">RoleListResponse</a></code>
- <code title="delete /admin/identity/roles/{id}">client.admin.identity.roles.<a href="./src/quarkupy/resources/admin/identity/roles/roles.py">delete</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>

#### Members

##### Identity

Methods:

- <code title="put /admin/identity/roles/{id}/members/identity/{identity_id}">client.admin.identity.roles.members.identity.<a href="./src/quarkupy/resources/admin/identity/roles/members/identity.py">add</a>(identity_id, \*, id) -> <a href="./src/quarkupy/types/admin/identity/identity_role.py">IdentityRole</a></code>
- <code title="delete /admin/identity/roles/{id}/members/identity/{identity_id}">client.admin.identity.roles.members.identity.<a href="./src/quarkupy/resources/admin/identity/roles/members/identity.py">remove</a>(identity_id, \*, id) -> <a href="./src/quarkupy/types/admin/identity/identity_role.py">IdentityRole</a></code>

##### Role

Methods:

- <code title="put /admin/identity/roles/{id}/members/role/{role_id}">client.admin.identity.roles.members.role.<a href="./src/quarkupy/resources/admin/identity/roles/members/role.py">add</a>(role_id, \*, id) -> <a href="./src/quarkupy/types/admin/identity/identity_role.py">IdentityRole</a></code>
- <code title="delete /admin/identity/roles/{id}/members/role/{role_id}">client.admin.identity.roles.members.role.<a href="./src/quarkupy/resources/admin/identity/roles/members/role.py">remove</a>(role_id, \*, id) -> <a href="./src/quarkupy/types/admin/identity/identity_role.py">IdentityRole</a></code>

# Models

Types:

```python
from quarkupy.types import MlModel, ModelListResponse
```

Methods:

- <code title="get /models/{id}">client.models.<a href="./src/quarkupy/resources/models/models.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/ml_model.py">MlModel</a></code>
- <code title="put /models">client.models.<a href="./src/quarkupy/resources/models/models.py">update</a>(\*\*<a href="src/quarkupy/types/model_update_params.py">params</a>) -> <a href="./src/quarkupy/types/ml_model.py">MlModel</a></code>
- <code title="get /models">client.models.<a href="./src/quarkupy/resources/models/models.py">list</a>() -> <a href="./src/quarkupy/types/model_list_response.py">ModelListResponse</a></code>
- <code title="delete /models/{id}">client.models.<a href="./src/quarkupy/resources/models/models.py">delete</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /models/schema">client.models.<a href="./src/quarkupy/resources/models/models.py">retrieve_schema</a>() -> object</code>
- <code title="patch /models/{id}">client.models.<a href="./src/quarkupy/resources/models/models.py">update_partial</a>(id, \*\*<a href="src/quarkupy/types/model_update_partial_params.py">params</a>) -> <a href="./src/quarkupy/types/ml_model.py">MlModel</a></code>

## Roles

Types:

```python
from quarkupy.types.models import MlModelRole, RoleListResponse
```

Methods:

- <code title="get /models/roles/{id}">client.models.roles.<a href="./src/quarkupy/resources/models/roles.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/models/ml_model_role.py">MlModelRole</a></code>
- <code title="put /models/roles">client.models.roles.<a href="./src/quarkupy/resources/models/roles.py">update</a>(\*\*<a href="src/quarkupy/types/models/role_update_params.py">params</a>) -> <a href="./src/quarkupy/types/models/ml_model_role.py">MlModelRole</a></code>
- <code title="get /models/roles">client.models.roles.<a href="./src/quarkupy/resources/models/roles.py">list</a>() -> <a href="./src/quarkupy/types/models/role_list_response.py">RoleListResponse</a></code>
- <code title="delete /models/roles/{id}">client.models.roles.<a href="./src/quarkupy/resources/models/roles.py">delete</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /models/roles/schema">client.models.roles.<a href="./src/quarkupy/resources/models/roles.py">retrieve_schema</a>() -> object</code>
- <code title="patch /models/roles/{id}">client.models.roles.<a href="./src/quarkupy/resources/models/roles.py">update_partial</a>(id, \*\*<a href="src/quarkupy/types/models/role_update_partial_params.py">params</a>) -> <a href="./src/quarkupy/types/models/ml_model_role.py">MlModelRole</a></code>

# Authorize

Methods:

- <code title="get /authorize">client.authorize.<a href="./src/quarkupy/resources/authorize.py">retrieve</a>(\*\*<a href="src/quarkupy/types/authorize_retrieve_params.py">params</a>) -> None</code>
- <code title="get /authorize/logout">client.authorize.<a href="./src/quarkupy/resources/authorize.py">logout</a>() -> None</code>

# Profile

## APIKeys

Types:

```python
from quarkupy.types.profile import APIKeyUpdateResponse, APIKeyListResponse
```

Methods:

- <code title="put /profile/api_keys">client.profile.api_keys.<a href="./src/quarkupy/resources/profile/api_keys.py">update</a>(\*\*<a href="src/quarkupy/types/profile/api_key_update_params.py">params</a>) -> <a href="./src/quarkupy/types/profile/api_key_update_response.py">APIKeyUpdateResponse</a></code>
- <code title="get /profile/api_keys">client.profile.api_keys.<a href="./src/quarkupy/resources/profile/api_keys.py">list</a>() -> <a href="./src/quarkupy/types/profile/api_key_list_response.py">APIKeyListResponse</a></code>
- <code title="delete /profile/api_keys/{id}">client.profile.api_keys.<a href="./src/quarkupy/resources/profile/api_keys.py">delete</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="patch /profile/api_keys/{id}/disable">client.profile.api_keys.<a href="./src/quarkupy/resources/profile/api_keys.py">disable</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /profile/api_keys/schema">client.profile.api_keys.<a href="./src/quarkupy/resources/profile/api_keys.py">retrieve_schema</a>() -> object</code>

# Sources

Types:

```python
from quarkupy.types import Source, SourceListResponse
```

Methods:

- <code title="get /sources/{id}">client.sources.<a href="./src/quarkupy/resources/sources.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/source.py">Source</a></code>
- <code title="put /sources">client.sources.<a href="./src/quarkupy/resources/sources.py">update</a>(\*\*<a href="src/quarkupy/types/source_update_params.py">params</a>) -> <a href="./src/quarkupy/types/source.py">Source</a></code>
- <code title="get /sources">client.sources.<a href="./src/quarkupy/resources/sources.py">list</a>() -> <a href="./src/quarkupy/types/source_list_response.py">SourceListResponse</a></code>
- <code title="delete /sources/{id}">client.sources.<a href="./src/quarkupy/resources/sources.py">delete</a>(id) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /sources/schema">client.sources.<a href="./src/quarkupy/resources/sources.py">retrieve_schema</a>() -> object</code>
- <code title="patch /sources/{id}">client.sources.<a href="./src/quarkupy/resources/sources.py">update_partial</a>(id, \*\*<a href="src/quarkupy/types/source_update_partial_params.py">params</a>) -> <a href="./src/quarkupy/types/source.py">Source</a></code>

# Users

Methods:

- <code title="get /users/me">client.users.<a href="./src/quarkupy/resources/users.py">retrieve_me</a>() -> <a href="./src/quarkupy/types/admin/identity/identity_model.py">IdentityModel</a></code>

# JsonSchemas

Types:

```python
from quarkupy.types import JsonSchemaListResponse
```

Methods:

- <code title="get /json_schemas">client.json_schemas.<a href="./src/quarkupy/resources/json_schemas.py">list</a>() -> <a href="./src/quarkupy/types/json_schema_list_response.py">JsonSchemaListResponse</a></code>

# History

Types:

```python
from quarkupy.types import HistoryListResponse, HistoryListFlowsResponse, HistoryListQuarksResponse
```

Methods:

- <code title="get /history">client.history.<a href="./src/quarkupy/resources/history/history.py">list</a>() -> <a href="./src/quarkupy/types/history_list_response.py">HistoryListResponse</a></code>
- <code title="get /history/clear_all_history">client.history.<a href="./src/quarkupy/resources/history/history.py">clear_all</a>() -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /history/flows">client.history.<a href="./src/quarkupy/resources/history/history.py">list_flows</a>(\*\*<a href="src/quarkupy/types/history_list_flows_params.py">params</a>) -> <a href="./src/quarkupy/types/history_list_flows_response.py">HistoryListFlowsResponse</a></code>
- <code title="get /history/quarks">client.history.<a href="./src/quarkupy/resources/history/history.py">list_quarks</a>(\*\*<a href="src/quarkupy/types/history_list_quarks_params.py">params</a>) -> <a href="./src/quarkupy/types/history_list_quarks_response.py">HistoryListQuarksResponse</a></code>

## Quark

Types:

```python
from quarkupy.types.history import QuarkHistoryItem
```

Methods:

- <code title="get /history/quark/{id}">client.history.quark.<a href="./src/quarkupy/resources/history/quark.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>
- <code title="put /history/quark">client.history.quark.<a href="./src/quarkupy/resources/history/quark.py">update</a>(\*\*<a href="src/quarkupy/types/history/quark_update_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

## Flow

Types:

```python
from quarkupy.types.history import FlowHistoryItem
```

Methods:

- <code title="get /history/flow/{id}">client.history.flow.<a href="./src/quarkupy/resources/history/flow.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/history/flow_history_item.py">FlowHistoryItem</a></code>
- <code title="put /history/flow">client.history.flow.<a href="./src/quarkupy/resources/history/flow.py">update</a>(\*\*<a href="src/quarkupy/types/history/flow_update_params.py">params</a>) -> <a href="./src/quarkupy/types/history/flow_history_item.py">FlowHistoryItem</a></code>

# Dataset

Types:

```python
from quarkupy.types import (
    DataSetInfo,
    DatasetListResponse,
    DatasetRetrieveCsvResponse,
    DatasetRetrieveJsonResponse,
)
```

Methods:

- <code title="get /dataset/{id}">client.dataset.<a href="./src/quarkupy/resources/dataset.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/data_set_info.py">DataSetInfo</a></code>
- <code title="get /dataset">client.dataset.<a href="./src/quarkupy/resources/dataset.py">list</a>() -> <a href="./src/quarkupy/types/dataset_list_response.py">DatasetListResponse</a></code>
- <code title="get /dataset/{id}/arrow">client.dataset.<a href="./src/quarkupy/resources/dataset.py">retrieve_arrow</a>(id, \*\*<a href="src/quarkupy/types/dataset_retrieve_arrow_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="get /dataset/{id}/{file_id}/chunks">client.dataset.<a href="./src/quarkupy/resources/dataset.py">retrieve_chunks</a>(file_id, \*, id, \*\*<a href="src/quarkupy/types/dataset_retrieve_chunks_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="get /dataset/{id}/csv">client.dataset.<a href="./src/quarkupy/resources/dataset.py">retrieve_csv</a>(id, \*\*<a href="src/quarkupy/types/dataset_retrieve_csv_params.py">params</a>) -> str</code>
- <code title="get /dataset/{id}/files">client.dataset.<a href="./src/quarkupy/resources/dataset.py">retrieve_files</a>(id, \*\*<a href="src/quarkupy/types/dataset_retrieve_files_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="get /dataset/{id}/json">client.dataset.<a href="./src/quarkupy/resources/dataset.py">retrieve_json</a>(id, \*\*<a href="src/quarkupy/types/dataset_retrieve_json_params.py">params</a>) -> str</code>

# Worker

## Management

Types:

```python
from quarkupy.types.worker import (
    ManagementRetrieveResponse,
    ManagementRetrievePythonStatusResponse,
    ManagementRetrieveTokioResponse,
)
```

Methods:

- <code title="get /worker/management">client.worker.management.<a href="./src/quarkupy/resources/worker/management.py">retrieve</a>() -> <a href="./src/quarkupy/types/worker/management_retrieve_response.py">ManagementRetrieveResponse</a></code>
- <code title="post /worker/management/ping">client.worker.management.<a href="./src/quarkupy/resources/worker/management.py">ping</a>() -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /worker/management/auth_status">client.worker.management.<a href="./src/quarkupy/resources/worker/management.py">retrieve_auth_status</a>() -> <a href="./src/quarkupy/types/admin/identity/identity_model.py">IdentityModel</a></code>
- <code title="get /worker/management/python_status">client.worker.management.<a href="./src/quarkupy/resources/worker/management.py">retrieve_python_status</a>() -> <a href="./src/quarkupy/types/worker/management_retrieve_python_status_response.py">ManagementRetrievePythonStatusResponse</a></code>
- <code title="get /worker/management/tokio">client.worker.management.<a href="./src/quarkupy/resources/worker/management.py">retrieve_tokio</a>(\*\*<a href="src/quarkupy/types/worker/management_retrieve_tokio_params.py">params</a>) -> <a href="./src/quarkupy/types/worker/management_retrieve_tokio_response.py">ManagementRetrieveTokioResponse</a></code>

## Agent

Types:

```python
from quarkupy.types.worker import AgentRetrieveResponse
```

Methods:

- <code title="get /worker/agent">client.worker.agent.<a href="./src/quarkupy/resources/worker/agent.py">retrieve</a>() -> <a href="./src/quarkupy/types/worker/agent_retrieve_response.py">AgentRetrieveResponse</a></code>
- <code title="post /worker/agent/chat_rag_demo">client.worker.agent.<a href="./src/quarkupy/resources/worker/agent.py">chat_rag_demo</a>(\*\*<a href="src/quarkupy/types/worker/agent_chat_rag_demo_params.py">params</a>) -> object</code>

## Registry

Types:

```python
from quarkupy.types.worker import RegistryListResponse
```

Methods:

- <code title="get /worker/registry">client.worker.registry.<a href="./src/quarkupy/resources/worker/registry/registry.py">list</a>() -> <a href="./src/quarkupy/types/worker/registry_list_response.py">RegistryListResponse</a></code>

### Quark

Types:

```python
from quarkupy.types.worker.registry import (
    DescribedInputField,
    QuarkRegistryItem,
    QuarkTag,
    SchemaInfo,
)
```

Methods:

- <code title="get /worker/registry/quark/{cat}/{name}">client.worker.registry.quark.<a href="./src/quarkupy/resources/worker/registry/quark/quark.py">retrieve</a>(name, \*, cat) -> <a href="./src/quarkupy/types/worker/registry/quark_registry_item.py">QuarkRegistryItem</a></code>

#### Files

##### S3ReadFilesBinary

Methods:

- <code title="post /worker/registry/quark/files/s3_read_files_binary/run">client.worker.registry.quark.files.s3_read_files_binary.<a href="./src/quarkupy/resources/worker/registry/quark/files/s3_read_files_binary.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/files/s3_read_files_binary_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### S3ReadCsv

Methods:

- <code title="post /worker/registry/quark/files/s3_read_csv/run">client.worker.registry.quark.files.s3_read_csv.<a href="./src/quarkupy/resources/worker/registry/quark/files/s3_read_csv.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/files/s3_read_csv_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### Opendal

Types:

```python
from quarkupy.types.worker.registry.quark.files import QuarkFileObjectStatus
```

Methods:

- <code title="post /worker/registry/quark/files/opendal/run">client.worker.registry.quark.files.opendal.<a href="./src/quarkupy/resources/worker/registry/quark/files/opendal.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/files/opendal_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>
- <code title="post /worker/registry/quark/files/opendal/schema">client.worker.registry.quark.files.opendal.<a href="./src/quarkupy/resources/worker/registry/quark/files/opendal.py">schema</a>() -> object</code>

#### Extractor

##### DoclingExtractor

Methods:

- <code title="post /worker/registry/quark/extractor/docling_extractor/run">client.worker.registry.quark.extractor.docling_extractor.<a href="./src/quarkupy/resources/worker/registry/quark/extractor/docling_extractor.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/extractor/docling_extractor_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

#### AI

##### OpenAIEmbeddings

Methods:

- <code title="post /worker/registry/quark/ai/openai_embeddings/run">client.worker.registry.quark.ai.openai_embeddings.<a href="./src/quarkupy/resources/worker/registry/quark/ai/openai_embeddings.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/ai/openai_embedding_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### OpenAICompletionBase

Methods:

- <code title="post /worker/registry/quark/ai/openai_completion_base/run">client.worker.registry.quark.ai.openai_completion_base.<a href="./src/quarkupy/resources/worker/registry/quark/ai/openai_completion_base.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/ai/openai_completion_base_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

#### Transformer

##### DoclingChunker

Methods:

- <code title="post /worker/registry/quark/transformer/docling_chunker/run">client.worker.registry.quark.transformer.docling_chunker.<a href="./src/quarkupy/resources/worker/registry/quark/transformer/docling_chunker.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/transformer/docling_chunker_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### HandlebarsBase

Methods:

- <code title="post /worker/registry/quark/transformer/handlebars_base/run">client.worker.registry.quark.transformer.handlebars_base.<a href="./src/quarkupy/resources/worker/registry/quark/transformer/handlebars_base.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/transformer/handlebars_base_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### OnnxSatSegmentation

Methods:

- <code title="post /worker/registry/quark/transformer/onnx_sat_segmentation/run">client.worker.registry.quark.transformer.onnx_sat_segmentation.<a href="./src/quarkupy/resources/worker/registry/quark/transformer/onnx_sat_segmentation.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/transformer/onnx_sat_segmentation_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### ContextExtractPrompt

Methods:

- <code title="post /worker/registry/quark/transformer/context_extract_prompt/run">client.worker.registry.quark.transformer.context_extract_prompt.<a href="./src/quarkupy/resources/worker/registry/quark/transformer/context_extract_prompt.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/transformer/context_extract_prompt_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### ParseExtractorLlm

Methods:

- <code title="post /worker/registry/quark/transformer/parse_extractor_llm/run">client.worker.registry.quark.transformer.parse_extractor_llm.<a href="./src/quarkupy/resources/worker/registry/quark/transformer/parse_extractor_llm.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/transformer/parse_extractor_llm_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### ContextClassifierPrompt

Methods:

- <code title="post /worker/registry/quark/transformer/context_classifier_prompt/run">client.worker.registry.quark.transformer.context_classifier_prompt.<a href="./src/quarkupy/resources/worker/registry/quark/transformer/context_classifier_prompt.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/transformer/context_classifier_prompt_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### ParseClassifierLlm

Methods:

- <code title="post /worker/registry/quark/transformer/parse_classifier_llm/run">client.worker.registry.quark.transformer.parse_classifier_llm.<a href="./src/quarkupy/resources/worker/registry/quark/transformer/parse_classifier_llm.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/transformer/parse_classifier_llm_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

#### Databases

##### SnowflakeRead

Methods:

- <code title="post /worker/registry/quark/databases/snowflake_read/run">client.worker.registry.quark.databases.snowflake_read.<a href="./src/quarkupy/resources/worker/registry/quark/databases/snowflake_read.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/databases/snowflake_read_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

#### Vector

##### LancedbIngest

Methods:

- <code title="post /worker/registry/quark/vector/lancedb_ingest/run">client.worker.registry.quark.vector.lancedb_ingest.<a href="./src/quarkupy/resources/worker/registry/quark/vector/lancedb_ingest.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/vector/lancedb_ingest_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### LancedbSearch

Methods:

- <code title="post /worker/registry/quark/vector/lancedb_search/run">client.worker.registry.quark.vector.lancedb_search.<a href="./src/quarkupy/resources/worker/registry/quark/vector/lancedb_search.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/vector/lancedb_search_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

#### Other

##### ContextInsertObjects

Methods:

- <code title="post /worker/registry/quark/other/context_insert_objects/run">client.worker.registry.quark.other.context_insert_objects.<a href="./src/quarkupy/resources/worker/registry/quark/other/context_insert_objects.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/other/context_insert_object_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### ContextInsertSegments

Methods:

- <code title="post /worker/registry/quark/other/context_insert_segments/run">client.worker.registry.quark.other.context_insert_segments.<a href="./src/quarkupy/resources/worker/registry/quark/other/context_insert_segments.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/other/context_insert_segment_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### ContextInsertClassifiedSegments

Methods:

- <code title="post /worker/registry/quark/other/context_insert_classified_segments/run">client.worker.registry.quark.other.context_insert_classified_segments.<a href="./src/quarkupy/resources/worker/registry/quark/other/context_insert_classified_segments.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/other/context_insert_classified_segment_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

##### ContextInsertExtractedSegments

Methods:

- <code title="post /worker/registry/quark/other/context_insert_extracted_segments/run">client.worker.registry.quark.other.context_insert_extracted_segments.<a href="./src/quarkupy/resources/worker/registry/quark/other/context_insert_extracted_segments.py">run</a>(\*\*<a href="src/quarkupy/types/worker/registry/quark/other/context_insert_extracted_segment_run_params.py">params</a>) -> <a href="./src/quarkupy/types/history/quark_history_item.py">QuarkHistoryItem</a></code>

### Lattice

Types:

```python
from quarkupy.types.worker.registry import (
    LatticeReactFlowPos,
    LatticeRegistryItem,
    LatticeRetrieveFlowResponse,
)
```

Methods:

- <code title="get /worker/registry/lattice/{id}">client.worker.registry.lattice.<a href="./src/quarkupy/resources/worker/registry/lattice.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/worker/registry/lattice_registry_item.py">LatticeRegistryItem</a></code>
- <code title="get /worker/registry/lattice/{id}/flow">client.worker.registry.lattice.<a href="./src/quarkupy/resources/worker/registry/lattice.py">retrieve_flow</a>(id) -> <a href="./src/quarkupy/types/worker/registry/lattice_retrieve_flow_response.py">LatticeRetrieveFlowResponse</a></code>
- <code title="put /worker/registry/lattice/register">client.worker.registry.lattice.<a href="./src/quarkupy/resources/worker/registry/lattice.py">update_register</a>(\*\*<a href="src/quarkupy/types/worker/registry/lattice_update_register_params.py">params</a>) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>

## Source

Types:

```python
from quarkupy.types.worker import SourceRetrieveListResponse
```

Methods:

- <code title="put /worker/source">client.worker.source.<a href="./src/quarkupy/resources/worker/source.py">create</a>(\*\*<a href="src/quarkupy/types/worker/source_create_params.py">params</a>) -> <a href="./src/quarkupy/types/source.py">Source</a></code>
- <code title="get /worker/source/{id}">client.worker.source.<a href="./src/quarkupy/resources/worker/source.py">retrieve</a>(id) -> <a href="./src/quarkupy/types/source.py">Source</a></code>
- <code title="get /worker/source">client.worker.source.<a href="./src/quarkupy/resources/worker/source.py">list</a>() -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /worker/source/{id}/add_all">client.worker.source.<a href="./src/quarkupy/resources/worker/source.py">retrieve_add_all</a>(id, \*\*<a href="src/quarkupy/types/worker/source_retrieve_add_all_params.py">params</a>) -> <a href="./src/quarkupy/types/context/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /worker/source/{id}/list">client.worker.source.<a href="./src/quarkupy/resources/worker/source.py">retrieve_list</a>(id, \*\*<a href="src/quarkupy/types/worker/source_retrieve_list_params.py">params</a>) -> <a href="./src/quarkupy/types/worker/source_retrieve_list_response.py">SourceRetrieveListResponse</a></code>

## Context

Methods:

- <code title="get /worker/context/files">client.worker.context.<a href="./src/quarkupy/resources/worker/context/context.py">retrieve_files</a>(\*\*<a href="src/quarkupy/types/worker/context_retrieve_files_params.py">params</a>) -> BinaryAPIResponse</code>

### Classifiers

Methods:

- <code title="get /worker/context/classifiers">client.worker.context.classifiers.<a href="./src/quarkupy/resources/worker/context/classifiers.py">list</a>(\*\*<a href="src/quarkupy/types/worker/context/classifier_list_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="get /worker/context/classifiers/{classifier_id}/text">client.worker.context.classifiers.<a href="./src/quarkupy/resources/worker/context/classifiers.py">retrieve_text</a>(classifier_id) -> BinaryAPIResponse</code>

### Extractors

Methods:

- <code title="get /worker/context/extractors">client.worker.context.extractors.<a href="./src/quarkupy/resources/worker/context/extractors.py">list</a>(\*\*<a href="src/quarkupy/types/worker/context/extractor_list_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="get /worker/context/extractors/{extractor_id}/text">client.worker.context.extractors.<a href="./src/quarkupy/resources/worker/context/extractors.py">retrieve_text</a>(extractor_id) -> BinaryAPIResponse</code>
