"""Generic regex-based fallback parser for other programming languages."""

import re
from pathlib import Path
from typing import List, Optional, Set

from repolens.parsers.base import (
    BaseParser,
    ParsedClass,
    ParsedFunction,
    ParsedImport,
    ParsedRoute,
    ParsedSource,
)


class GenericParser(BaseParser):
    """Fallback parser for Java, C, C++, C#, PHP, Ruby, Kotlin, Swift, Shell, etc."""

    # Common import / include patterns
    IMPORT_PATTERNS = [
        re.compile(r'^\s*import\s+([a-zA-Z0-9_.*]+);?', re.MULTILINE),  # Java, Kotlin, C#
        re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]', re.MULTILINE),  # C/C++
        re.compile(r'^\s*using\s+([a-zA-Z0-9_.]+);', re.MULTILINE),  # C#
        re.compile(r'^\s*require(?:_relative)?\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE),  # Ruby
        re.compile(r'^\s*use\s+([a-zA-Z0-9_\\]+);', re.MULTILINE),  # PHP
        re.compile(r'^\s*source\s+([^\s]+)', re.MULTILINE),  # Shell
    ]

    CLASS_PATTERNS = [
        re.compile(r'(?:public\s+|private\s+|protected\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?', re.MULTILINE),
        re.compile(r'struct\s+(\w+)', re.MULTILINE),
    ]

    ENV_PATTERNS = [
        re.compile(r'System\.getenv\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)'),  # Java
        re.compile(r'Environment\.GetEnvironmentVariable\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)'),  # C#
        re.compile(r'getenv\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)'),  # C/PHP
        re.compile(r'ENV\[[\'"]([A-Z0-9_]+)[\'"]\]'),  # Ruby
        re.compile(r'\$\{?([A-Z0-9_]{3,})\}?'),  # Shell
    ]

    # Spring Boot / Rails / Laravel routes
    SPRING_ROUTE = re.compile(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*\(\s*(?:(?:value|path)\s*=\s*)?[\'"]([^\'"]+)[\'"]', re.IGNORECASE)

    def can_parse(self, file_path: Path) -> bool:
        return True

    def parse(self, file_path: Path, content: str, rel_path: str) -> ParsedSource:
        ext = file_path.suffix.lower()
        lang_map = {
            ".java": "Java",
            ".kt": "Kotlin",
            ".cs": "C#",
            ".cpp": "C++",
            ".c": "C",
            ".h": "C/C++ Header",
            ".hpp": "C++ Header",
            ".php": "PHP",
            ".rb": "Ruby",
            ".swift": "Swift",
            ".sh": "Shell",
            ".bash": "Shell",
            ".zsh": "Shell",
            ".ps1": "PowerShell",
            ".sql": "SQL",
            ".html": "HTML",
            ".css": "CSS",
        }
        lang = lang_map.get(ext, "Unknown")

        imports: List[ParsedImport] = []
        classes: List[ParsedClass] = []
        routes: List[ParsedRoute] = []
        env_vars: Set[str] = set()

        # Imports
        for pattern in self.IMPORT_PATTERNS:
            for match in pattern.finditer(content):
                imports.append(
                    ParsedImport(
                        module=match.group(1),
                        line_number=content[: match.start()].count("\n") + 1,
                    )
                )

        # Classes
        for pattern in self.CLASS_PATTERNS:
            for match in pattern.finditer(content):
                cls_name = match.group(1)
                bases = [match.group(2)] if len(match.groups()) > 1 and match.group(2) else []
                classes.append(
                    ParsedClass(
                        name=cls_name,
                        base_classes=bases,
                        line_number=content[: match.start()].count("\n") + 1,
                    )
                )

        # Spring Boot routes
        for match in self.SPRING_ROUTE.finditer(content):
            method_ann = match.group(1).replace("Mapping", "").upper()
            if method_ann == "REQUEST":
                method_ann = "ALL"
            route_path = match.group(2)
            routes.append(
                ParsedRoute(
                    path=route_path,
                    http_method=method_ann,
                    handler_name="controller_method",
                    framework="Spring Boot",
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        # Env vars
        for pattern in self.ENV_PATTERNS:
            for match in pattern.finditer(content):
                v = match.group(1)
                if v and not v.startswith("_") and len(v) >= 3:
                    env_vars.add(v)

        return ParsedSource(
            file_path=rel_path,
            language=lang,
            imports=imports,
            classes=classes,
            routes=routes,
            env_vars=sorted(list(env_vars)),
            syntax_valid=True,
        )
