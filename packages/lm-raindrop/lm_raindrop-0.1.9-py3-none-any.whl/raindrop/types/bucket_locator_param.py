# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = ["BucketLocatorParam", "Bucket", "BucketBucket", "ModuleID"]


class BucketBucket(TypedDict, total=False):
    name: Required[str]
    """The name of the bucket **EXAMPLE** "my-bucket" **REQUIRED** TRUE"""

    application_name: Annotated[Optional[str], PropertyInfo(alias="applicationName")]
    """Optional Application **EXAMPLE** "my-app" **REQUIRED** FALSE"""

    version: Optional[str]
    """
    Optional version of the bucket **EXAMPLE** "01jtryx2f2f61ryk06vd8mr91p"
    **REQUIRED** FALSE
    """


class Bucket(TypedDict, total=False):
    bucket: Required[BucketBucket]
    """**EXAMPLE** { name: 'my-smartbucket' } **REQUIRED** FALSE"""


class ModuleID(TypedDict, total=False):
    module_id: Required[Annotated[str, PropertyInfo(alias="moduleId")]]
    """**EXAMPLE** "01jtryx2f2f61ryk06vd8mr91p" **REQUIRED** FALSE"""


BucketLocatorParam: TypeAlias = Union[Bucket, ModuleID]
