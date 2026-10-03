"""Base AST and source code parser interfaces and models."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class ParsedImport(BaseModel):
    module: str
    imported_names: List[str] = Field(default_factory=list)
    alias: Optional[str] = None
    is_relative: bool = False
    line_number: int = 1


class ParsedFunction(BaseModel):
    name: str
    args: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    is_async: bool = False
    decorators: List[str] = Field(default_factory=list)
    line_number: int = 1
    docstring: Optional[str] = None
    calls: List[str] = Field(default_factory=list)


class ParsedClass(BaseModel):
    name: str
    base_classes: List[str] = Field(default_factory=list)
    methods: List[ParsedFunction] = Field(default_factory=list)
    fields: List[str] = Field(default_factory=list)
    line_number: int = 1
    docstring: Optional[str] = None


class ParsedRoute(BaseModel):
    path: str
    http_method: str  # GET, POST, PUT, DELETE, PATCH, etc.
    handler_name: str
    framework: str  # fastapi, flask, express, nextjs, django, gin, actix, etc.
    line_number: int = 1
    parameters: List[str] = Field(default_factory=list)
    auth_required: bool = False


class ParsedSource(BaseModel):
    file_path: str
    language: str
    imports: List[ParsedImport] = Field(default_factory=list)
    classes: List[ParsedClass] = Field(default_factory=list)
    functions: List[ParsedFunction] = Field(default_factory=list)
    routes: List[ParsedRoute] = Field(default_factory=list)
    env_vars: List[str] = Field(default_factory=list)
    db_models: List[str] = Field(default_factory=list)
    syntax_valid: bool = True
    error_message: Optional[str] = None


class BaseParser(ABC):
    """Abstract base class for language source code parsers."""

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Return True if this parser can handle the given file."""
        pass

    @abstractmethod
    def parse(self, file_path: Path, content: str, rel_path: str) -> ParsedSource:
        """Parse source code content and extract structured symbols."""
        pass
