# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["QueryChunkSearchResponse", "Result", "ResultSource", "ResultSourceBucket"]


class ResultSourceBucket(BaseModel):
    application_name: Optional[str] = FieldInfo(alias="applicationName", default=None)
    """**EXAMPLE** "my-app" """

    application_version_id: Optional[str] = FieldInfo(alias="applicationVersionId", default=None)
    """**EXAMPLE** "01jtryx2f2f61ryk06vd8mr91p" """

    bucket_name: Optional[str] = FieldInfo(alias="bucketName", default=None)
    """**EXAMPLE** "my-smartbucket" """

    module_id: Optional[str] = FieldInfo(alias="moduleId", default=None)
    """**EXAMPLE** "01jtryx2f2f61ryk06vd8mr91p" """


class ResultSource(BaseModel):
    bucket: Optional[ResultSourceBucket] = None
    """The bucket information containing this result"""

    object: Optional[str] = None
    """The object key within the bucket"""


class Result(BaseModel):
    chunk_signature: Optional[str] = FieldInfo(alias="chunkSignature", default=None)
    """Unique identifier for this text segment.

    Used for deduplication and result tracking
    """

    embed: Optional[str] = None
    """Vector representation for similarity matching.

    Used in semantic search operations
    """

    payload_signature: Optional[str] = FieldInfo(alias="payloadSignature", default=None)
    """Parent document identifier. Links related content chunks together"""

    score: Optional[float] = None
    """Relevance score (0.0 to 1.0). Higher scores indicate better matches"""

    source: Optional[ResultSource] = None
    """Source document references. Contains bucket and object information"""

    text: Optional[str] = None
    """The actual content of the result. May be a document excerpt or full content"""

    type: Optional[str] = None
    """Content MIME type. Helps with proper result rendering"""


class QueryChunkSearchResponse(BaseModel):
    results: Optional[List[Result]] = None
    """Ordered list of relevant text segments.

    Each result includes full context and metadata
    """
