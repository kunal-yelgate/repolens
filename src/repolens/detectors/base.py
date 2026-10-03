"""Base detector interfaces and data models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory


class FindingEvidence(BaseModel):
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    observation: str
    confidence: float = 1.0


class EntryPointInfo(BaseModel):
    file: str
    type: str  # application, cli, web_server, script, worker
    confidence: float
    reason: str
    evidence: List[str] = Field(default_factory=list)


class DatabaseInfo(BaseModel):
    technology: str  # PostgreSQL, SQLite, MySQL, MongoDB, Redis, etc.
    orm: Optional[str] = None  # SQLAlchemy, Prisma, Mongoose, etc.
    confidence: float
    models: List[str] = Field(default_factory=list)
    config_files: List[str] = Field(default_factory=list)
    migrations_dir: Optional[str] = None


class ArchitectureFinding(BaseModel):
    architecture: str
    confidence: float
    evidence: List[str] = Field(default_factory=list)
    source_dirs: List[str] = Field(default_factory=list)


class EnvVarInfo(BaseModel):
    name: str
    required: bool = True
    used_in_files: List[str] = Field(default_factory=list)
    default_value: Optional[str] = None
    description: Optional[str] = None


class TestFrameworkInfo(BaseModel):
    framework: str  # pytest, jest, vitest, go_test, cargo_test, etc.
    test_dirs: List[str] = Field(default_factory=list)
    test_files_count: int = 0
    run_all_command: str
    run_single_command_template: str


class ProjectCommandsInfo(BaseModel):
    install: Dict[str, str] = Field(default_factory=dict)  # {"Backend": "pip install -r ...", "Frontend": "npm install"}
    dev: Dict[str, str] = Field(default_factory=dict)  # {"Backend": "uvicorn ...", "Frontend": "npm run dev"}
    test: Dict[str, str] = Field(default_factory=dict)  # {"All": "pytest"}
    build: Dict[str, str] = Field(default_factory=dict)


class ArchitecturalConcern(BaseModel):
    title: str
    category: str  # circular_dependency, god_file, coupling, missing_tests, secret_risk, etc.
    file: Optional[str] = None
    observation: str
    confidence: float
    suggested_action: str


class BaseDetector(ABC):
    """Abstract base detector interface."""

    @abstractmethod
    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> Any:
        pass
