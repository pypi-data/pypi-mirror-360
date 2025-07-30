# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "PutMemoryCreateParams",
    "AgentMemoryLocation",
    "AgentMemoryLocationAgentMemory",
    "AgentMemoryLocationAgentMemoryAgentMemory",
    "AgentMemoryLocationModuleID",
]


class PutMemoryCreateParams(TypedDict, total=False):
    agent_memory_location: Required[Annotated[AgentMemoryLocation, PropertyInfo(alias="agentMemoryLocation")]]
    """Agent memory locator for targeting the correct agent memory instance"""

    content: Required[str]
    """The actual memory content to store"""

    session_id: Required[Annotated[str, PropertyInfo(alias="sessionId")]]
    """Unique session identifier for the working memory instance"""

    agent: Optional[str]
    """Agent identifier responsible for this memory"""

    key: Optional[str]
    """Optional key for direct memory retrieval"""

    timeline: Optional[str]
    """Timeline identifier for organizing related memories"""


class AgentMemoryLocationAgentMemoryAgentMemory(TypedDict, total=False):
    name: Required[str]
    """The name of the agent memory **EXAMPLE** "my-agent-memory" **REQUIRED** TRUE"""

    application_name: Annotated[Optional[str], PropertyInfo(alias="applicationName")]
    """Optional Application **EXAMPLE** "my-app" **REQUIRED** FALSE"""

    version: Optional[str]
    """
    Optional version of the agent memory **EXAMPLE** "01jtryx2f2f61ryk06vd8mr91p"
    **REQUIRED** FALSE
    """


class AgentMemoryLocationAgentMemory(TypedDict, total=False):
    agent_memory: Required[Annotated[AgentMemoryLocationAgentMemoryAgentMemory, PropertyInfo(alias="agentMemory")]]
    """
    **EXAMPLE** {"name":"memory-name","application_name":"demo","version":"1234"}
    **REQUIRED** FALSE
    """


class AgentMemoryLocationModuleID(TypedDict, total=False):
    module_id: Required[Annotated[str, PropertyInfo(alias="moduleId")]]


AgentMemoryLocation: TypeAlias = Union[AgentMemoryLocationAgentMemory, AgentMemoryLocationModuleID]
