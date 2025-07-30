# Query

Types:

```python
from raindrop.types import (
    BucketLocator,
    QueryChunkSearchResponse,
    QueryDocumentQueryResponse,
    QueryGetPaginatedSearchResponse,
    QuerySearchResponse,
    QuerySumarizePageResponse,
)
```

Methods:

- <code title="post /v1/chunk_search">client.query.<a href="./src/raindrop/resources/query/query.py">chunk_search</a>(\*\*<a href="src/raindrop/types/query_chunk_search_params.py">params</a>) -> <a href="./src/raindrop/types/query_chunk_search_response.py">QueryChunkSearchResponse</a></code>
- <code title="post /v1/document_query">client.query.<a href="./src/raindrop/resources/query/query.py">document_query</a>(\*\*<a href="src/raindrop/types/query_document_query_params.py">params</a>) -> <a href="./src/raindrop/types/query_document_query_response.py">QueryDocumentQueryResponse</a></code>
- <code title="post /v1/search_get_page">client.query.<a href="./src/raindrop/resources/query/query.py">get_paginated_search</a>(\*\*<a href="src/raindrop/types/query_get_paginated_search_params.py">params</a>) -> <a href="./src/raindrop/types/query_get_paginated_search_response.py">SyncPageNumber[QueryGetPaginatedSearchResponse]</a></code>
- <code title="post /v1/search">client.query.<a href="./src/raindrop/resources/query/query.py">search</a>(\*\*<a href="src/raindrop/types/query_search_params.py">params</a>) -> <a href="./src/raindrop/types/query_search_response.py">QuerySearchResponse</a></code>
- <code title="post /v1/summarize_page">client.query.<a href="./src/raindrop/resources/query/query.py">sumarize_page</a>(\*\*<a href="src/raindrop/types/query_sumarize_page_params.py">params</a>) -> <a href="./src/raindrop/types/query_sumarize_page_response.py">QuerySumarizePageResponse</a></code>

## Memory

Types:

```python
from raindrop.types.query import MemorySearchResponse
```

Methods:

- <code title="post /v1/search_memory">client.query.memory.<a href="./src/raindrop/resources/query/memory.py">search</a>(\*\*<a href="src/raindrop/types/query/memory_search_params.py">params</a>) -> <a href="./src/raindrop/types/query/memory_search_response.py">MemorySearchResponse</a></code>

# Bucket

Types:

```python
from raindrop.types import BucketListResponse, BucketGetResponse, BucketPutResponse
```

Methods:

- <code title="post /v1/list_objects">client.bucket.<a href="./src/raindrop/resources/bucket.py">list</a>(\*\*<a href="src/raindrop/types/bucket_list_params.py">params</a>) -> <a href="./src/raindrop/types/bucket_list_response.py">BucketListResponse</a></code>
- <code title="post /v1/delete_object">client.bucket.<a href="./src/raindrop/resources/bucket.py">delete</a>(\*\*<a href="src/raindrop/types/bucket_delete_params.py">params</a>) -> object</code>
- <code title="post /v1/get_object">client.bucket.<a href="./src/raindrop/resources/bucket.py">get</a>(\*\*<a href="src/raindrop/types/bucket_get_params.py">params</a>) -> <a href="./src/raindrop/types/bucket_get_response.py">BucketGetResponse</a></code>
- <code title="post /v1/put_object">client.bucket.<a href="./src/raindrop/resources/bucket.py">put</a>(\*\*<a href="src/raindrop/types/bucket_put_params.py">params</a>) -> <a href="./src/raindrop/types/bucket_put_response.py">BucketPutResponse</a></code>

# PutMemory

Types:

```python
from raindrop.types import PutMemoryCreateResponse
```

Methods:

- <code title="post /v1/put_memory">client.put_memory.<a href="./src/raindrop/resources/put_memory.py">create</a>(\*\*<a href="src/raindrop/types/put_memory_create_params.py">params</a>) -> <a href="./src/raindrop/types/put_memory_create_response.py">PutMemoryCreateResponse</a></code>

# GetMemory

Types:

```python
from raindrop.types import GetMemoryRetrieveResponse
```

Methods:

- <code title="post /v1/get_memory">client.get_memory.<a href="./src/raindrop/resources/get_memory.py">retrieve</a>(\*\*<a href="src/raindrop/types/get_memory_retrieve_params.py">params</a>) -> <a href="./src/raindrop/types/get_memory_retrieve_response.py">GetMemoryRetrieveResponse</a></code>

# DeleteMemory

Types:

```python
from raindrop.types import DeleteMemoryCreateResponse
```

Methods:

- <code title="post /v1/delete_memory">client.delete_memory.<a href="./src/raindrop/resources/delete_memory.py">create</a>(\*\*<a href="src/raindrop/types/delete_memory_create_params.py">params</a>) -> <a href="./src/raindrop/types/delete_memory_create_response.py">DeleteMemoryCreateResponse</a></code>

# SummarizeMemory

Types:

```python
from raindrop.types import SummarizeMemoryCreateResponse
```

Methods:

- <code title="post /v1/summarize_memory">client.summarize_memory.<a href="./src/raindrop/resources/summarize_memory.py">create</a>(\*\*<a href="src/raindrop/types/summarize_memory_create_params.py">params</a>) -> <a href="./src/raindrop/types/summarize_memory_create_response.py">SummarizeMemoryCreateResponse</a></code>

# StartSession

Types:

```python
from raindrop.types import StartSessionCreateResponse
```

Methods:

- <code title="post /v1/start_session">client.start_session.<a href="./src/raindrop/resources/start_session.py">create</a>(\*\*<a href="src/raindrop/types/start_session_create_params.py">params</a>) -> <a href="./src/raindrop/types/start_session_create_response.py">StartSessionCreateResponse</a></code>

# EndSession

Types:

```python
from raindrop.types import EndSessionCreateResponse
```

Methods:

- <code title="post /v1/end_session">client.end_session.<a href="./src/raindrop/resources/end_session.py">create</a>(\*\*<a href="src/raindrop/types/end_session_create_params.py">params</a>) -> <a href="./src/raindrop/types/end_session_create_response.py">EndSessionCreateResponse</a></code>

# RehydrateSession

Types:

```python
from raindrop.types import RehydrateSessionRehydrateResponse
```

Methods:

- <code title="post /v1/rehydrate_session">client.rehydrate_session.<a href="./src/raindrop/resources/rehydrate_session.py">rehydrate</a>(\*\*<a href="src/raindrop/types/rehydrate_session_rehydrate_params.py">params</a>) -> <a href="./src/raindrop/types/rehydrate_session_rehydrate_response.py">RehydrateSessionRehydrateResponse</a></code>
