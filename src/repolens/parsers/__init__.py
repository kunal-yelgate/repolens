"""Parsers module for source code analysis."""

from pathlib import Path
from typing import List

from repolens.parsers.base import (
    BaseParser,
    ParsedClass,
    ParsedFunction,
    ParsedImport,
    ParsedRoute,
    ParsedSource,
)
from repolens.parsers.generic import GenericParser
from repolens.parsers.go import GoParser, RustParser
from repolens.parsers.javascript import JavaScriptParser
from repolens.parsers.python import PythonParser

_PARSERS: List[BaseParser] = [
    PythonParser(),
    JavaScriptParser(),
    GoParser(),
    RustParser(),
    GenericParser(),
]


def get_parser_for_file(file_path: Path) -> BaseParser:
    """Get the appropriate parser instance for a given file."""
    for parser in _PARSERS:
        if parser.can_parse(file_path):
            return parser
    return _PARSERS[-1]  # Fallback to GenericParser


__all__ = [
    "BaseParser",
    "ParsedImport",
    "ParsedFunction",
    "ParsedClass",
    "ParsedRoute",
    "ParsedSource",
    "PythonParser",
    "JavaScriptParser",
    "GoParser",
    "RustParser",
    "GenericParser",
    "get_parser_for_file",
]
