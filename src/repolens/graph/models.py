"""Entity and relationship models for the Repository Knowledge Graph."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    REPOSITORY = "Repository"
    DIRECTORY = "Directory"
    FILE = "File"
    CLASS = "Class"
    FUNCTION = "Function"
    MODULE = "Module"
    API = "API"
    DATABASE = "Database"
    ENVIRONMENT_VARIABLE = "EnvironmentVariable"
    DEPENDENCY = "Dependency"
    TEST = "Test"
    CONFIGURATION = "Configuration"
    EXTERNAL_SERVICE = "ExternalService"


class RelationType(str, Enum):
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    CONTAINS = "CONTAINS"
    DEPENDS_ON = "DEPENDS_ON"
    EXPOSES = "EXPOSES"
    USES = "USES"
    CONFIGURES = "CONFIGURES"
    TESTS = "TESTS"
    CONNECTS_TO = "CONNECTS_TO"


class GraphNode(BaseModel):
    id: str
    label: str
    entity_type: EntityType
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: RelationType
    properties: Dict[str, Any] = Field(default_factory=dict)
