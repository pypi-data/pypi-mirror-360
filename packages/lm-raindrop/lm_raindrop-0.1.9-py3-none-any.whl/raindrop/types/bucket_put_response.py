# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["BucketPutResponse", "Bucket"]


class Bucket(BaseModel):
    application_name: Optional[str] = FieldInfo(alias="applicationName", default=None)
    """**EXAMPLE** "my-app" """

    application_version_id: Optional[str] = FieldInfo(alias="applicationVersionId", default=None)
    """**EXAMPLE** "01jtryx2f2f61ryk06vd8mr91p" """

    bucket_name: Optional[str] = FieldInfo(alias="bucketName", default=None)
    """**EXAMPLE** "my-smartbucket" """

    module_id: Optional[str] = FieldInfo(alias="moduleId", default=None)
    """**EXAMPLE** "01jtryx2f2f61ryk06vd8mr91p" """


class BucketPutResponse(BaseModel):
    bucket: Optional[Bucket] = None
    """Information about the bucket where the object was uploaded"""

    key: Optional[str] = None
    """Key/path of the uploaded object"""
