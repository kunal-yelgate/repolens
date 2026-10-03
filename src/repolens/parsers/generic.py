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
    """Fallback parser for Java, C, C++, C#, PHP, Ruby, Kotlin, Swift, Shell, Dart, Scala, Elixir, etc."""

    # Common import / include patterns
    IMPORT_PATTERNS = [
        re.compile(r'^\s*import\s+([a-zA-Z0-9_.*]+);?', re.MULTILINE),  # Java, Kotlin, C#, Dart, Swift
        re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]', re.MULTILINE),  # C/C++
        re.compile(r'^\s*using\s+([a-zA-Z0-9_.]+);', re.MULTILINE),  # C#
        re.compile(r'^\s*require(?:_relative)?\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE),  # Ruby
        re.compile(r'^\s*use\s+([a-zA-Z0-9_\\]+);', re.MULTILINE),  # PHP, Rust
        re.compile(r'^\s*source\s+([^\s]+)', re.MULTILINE),  # Shell
        re.compile(r'^\s*alias\s+([a-zA-Z0-9_.]+)', re.MULTILINE),  # Elixir
    ]

    CLASS_PATTERNS = [
        re.compile(r'(?:public\s+|private\s+|protected\s+|abstract\s+|final\s+)*(?:class|interface|enum|record|trait|struct)\s+(\w+)(?:\s+extends\s+(\w+))?', re.MULTILINE),
        re.compile(r'struct\s+(\w+)', re.MULTILINE),
    ]

    FUNCTION_PATTERNS = [
        re.compile(r'(?:fun|func|fn)\s+(\w+)\s*\(', re.MULTILINE),  # Kotlin, Swift, Go, Rust
        re.compile(r'def\s+(\w+)', re.MULTILINE),  # Ruby, Elixir, Python
        re.compile(r'function\s+(\w+)', re.MULTILINE),  # PHP, JS, Shell
        re.compile(r'(?:public|private|protected|static|final|async|virtual|override|\s)+[\w<>\[\]\?]+\s+(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE),  # Java, C#, C++
        re.compile(r'^\s*(?:function\s+)?([a-zA-Z0-9_-]+)\s*\(\)\s*\{', re.MULTILINE),  # Shell
    ]

    ENV_PATTERNS = [
        re.compile(r'System\.getenv\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)'),  # Java
        re.compile(r'Environment\.GetEnvironmentVariable\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)'),  # C#
        re.compile(r'getenv\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)'),  # C/PHP
        re.compile(r'ENV\[[\'"]([A-Z0-9_]+)[\'"]\]'),  # Ruby
        re.compile(r'\$\{?([A-Z0-9_]{3,})\}?'),  # Shell
        re.compile(r'Platform\.environment\[[\'"]([A-Z0-9_]+)[\'"]\]'),  # Dart
    ]

    # Spring Boot / ASP.NET / Laravel / Rails / Express routes
    SPRING_ROUTE = re.compile(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(\s*(?:(?:value|path)\s*=\s*)?[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
    ASPNET_ROUTE = re.compile(r'\[(HttpGet|HttpPost|HttpPut|HttpDelete|HttpPatch|Route)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)\]', re.IGNORECASE)
    LARAVEL_ROUTE = re.compile(r'Route::(get|post|put|delete|patch|any)\s*\(\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
    EXPRESS_ROUTE = re.compile(r'(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)

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
            ".dart": "Dart",
            ".scala": "Scala",
            ".ex": "Elixir",
            ".exs": "Elixir",
            ".erl": "Erlang",
            ".zig": "Zig",
        }
        lang = lang_map.get(ext, "Unknown")

        imports: List[ParsedImport] = []
        classes: List[ParsedClass] = []
        functions: List[ParsedFunction] = []
        routes: List[ParsedRoute] = []
        db_models: List[str] = []
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
        seen_classes = set()
        for pattern in self.CLASS_PATTERNS:
            for match in pattern.finditer(content):
                cls_name = match.group(1)
                if cls_name not in seen_classes and cls_name not in {"if", "for", "while", "switch"}:
                    seen_classes.add(cls_name)
                    bases = [match.group(2)] if len(match.groups()) > 1 and match.group(2) else []
                    classes.append(
                        ParsedClass(
                            name=cls_name,
                            base_classes=bases,
                            line_number=content[: match.start()].count("\n") + 1,
                        )
                    )
                    # Check for ORM / DB annotations or inheritance
                    if "Entity" in content or "Table" in content or "Document" in content or "Model" in content or "DbContext" in content:
                        db_models.append(cls_name)

        # Functions
        seen_funcs = set()
        for pattern in self.FUNCTION_PATTERNS:
            for match in pattern.finditer(content):
                fn_name = match.group(1)
                if fn_name not in seen_funcs and fn_name not in {"if", "for", "while", "switch", "catch", "return", "class", "struct"}:
                    seen_funcs.add(fn_name)
                    functions.append(
                        ParsedFunction(
                            name=fn_name,
                            line_number=content[: match.start()].count("\n") + 1,
                        )
                    )

        # Spring Boot routes
        for match in self.SPRING_ROUTE.finditer(content):
            method_ann = match.group(1).replace("Mapping", "").upper()
            if method_ann == "REQUEST":
                method_ann = "ALL"
            routes.append(
                ParsedRoute(
                    path=match.group(2),
                    http_method=method_ann,
                    handler_name="controller_method",
                    framework="Spring Boot",
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        # ASP.NET routes
        for match in self.ASPNET_ROUTE.finditer(content):
            method_ann = match.group(1).replace("Http", "").upper()
            if method_ann == "ROUTE":
                method_ann = "GET"
            routes.append(
                ParsedRoute(
                    path=match.group(2),
                    http_method=method_ann,
                    handler_name="action_method",
                    framework="ASP.NET Core",
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        # Laravel routes
        for match in self.LARAVEL_ROUTE.finditer(content):
            routes.append(
                ParsedRoute(
                    path=match.group(2),
                    http_method=match.group(1).upper(),
                    handler_name="action",
                    framework="Laravel",
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        # Express routes
        for match in self.EXPRESS_ROUTE.finditer(content):
            routes.append(
                ParsedRoute(
                    path=match.group(2),
                    http_method=match.group(1).upper(),
                    handler_name="route_handler",
                    framework="Express/Koa",
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
            functions=functions,
            routes=routes,
            db_models=db_models,
            env_vars=sorted(list(env_vars)),
            syntax_valid=True,
        )
