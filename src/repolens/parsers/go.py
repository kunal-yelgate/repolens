"""Go and Rust source code parsers."""

import re
from pathlib import Path
from typing import List, Set

from repolens.parsers.base import (
    BaseParser,
    ParsedClass,
    ParsedFunction,
    ParsedImport,
    ParsedRoute,
    ParsedSource,
)


class GoParser(BaseParser):
    """Parses Go source files."""

    IMPORT_SINGLE = re.compile(r'import\s+[\'"]([^\'"]+)[\'"]')
    IMPORT_BLOCK = re.compile(r'import\s*\(([^)]+)\)', re.MULTILINE)
    FUNC_DECL = re.compile(r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)', re.MULTILINE)
    STRUCT_DECL = re.compile(r'type\s+(\w+)\s+struct\s*\{', re.MULTILINE)
    GIN_ROUTE = re.compile(r'(?:r|router|api|v1|g)\.(GET|POST|PUT|DELETE|PATCH)\s*\(\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
    ENV_PATTERN = re.compile(r'os\.Getenv\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)|os\.LookupEnv\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)')

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".go"

    def parse(self, file_path: Path, content: str, rel_path: str) -> ParsedSource:
        imports: List[ParsedImport] = []
        classes: List[ParsedClass] = []
        functions: List[ParsedFunction] = []
        routes: List[ParsedRoute] = []
        env_vars: Set[str] = set()

        for match in self.IMPORT_SINGLE.finditer(content):
            imports.append(ParsedImport(module=match.group(1), line_number=content[: match.start()].count("\n") + 1))

        for match in self.IMPORT_BLOCK.finditer(content):
            block = match.group(1)
            for line in block.splitlines():
                cleaned = line.strip().strip('"').strip("'")
                if cleaned:
                    mod = cleaned.split()[-1].strip('"').strip("'")
                    imports.append(ParsedImport(module=mod, line_number=content[: match.start()].count("\n") + 1))

        for match in self.FUNC_DECL.finditer(content):
            functions.append(
                ParsedFunction(
                    name=match.group(1),
                    args=[a.strip() for a in match.group(2).split(",") if a.strip()],
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        for match in self.STRUCT_DECL.finditer(content):
            classes.append(
                ParsedClass(
                    name=match.group(1),
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        for match in self.GIN_ROUTE.finditer(content):
            routes.append(
                ParsedRoute(
                    path=match.group(2),
                    http_method=match.group(1).upper(),
                    handler_name="gin_handler",
                    framework="Gin",
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        for match in self.ENV_PATTERN.finditer(content):
            v = match.group(1) or match.group(2)
            if v:
                env_vars.add(v)

        return ParsedSource(
            file_path=rel_path,
            language="Go",
            imports=imports,
            classes=classes,
            functions=functions,
            routes=routes,
            env_vars=sorted(list(env_vars)),
            syntax_valid=True,
        )


class RustParser(BaseParser):
    """Parses Rust source files."""

    USE_STMT = re.compile(r'use\s+([^;]+);', re.MULTILINE)
    FN_DECL = re.compile(r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(([^)]*)\)', re.MULTILINE)
    STRUCT_DECL = re.compile(r'(?:pub\s+)?struct\s+(\w+)', re.MULTILINE)
    ACTIX_ROUTE = re.compile(r'#\[(?:get|post|put|delete)\("([^"]+)"\)\]', re.IGNORECASE)
    ENV_PATTERN = re.compile(r'env::var\(\s*[\'"]([A-Z0-9_]+)[\'"]\s*\)')

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".rs"

    def parse(self, file_path: Path, content: str, rel_path: str) -> ParsedSource:
        imports: List[ParsedImport] = []
        classes: List[ParsedClass] = []
        functions: List[ParsedFunction] = []
        routes: List[ParsedRoute] = []
        env_vars: Set[str] = set()

        for match in self.USE_STMT.finditer(content):
            imports.append(ParsedImport(module=match.group(1).strip(), line_number=content[: match.start()].count("\n") + 1))

        for match in self.FN_DECL.finditer(content):
            functions.append(
                ParsedFunction(
                    name=match.group(1),
                    args=[a.strip() for a in match.group(2).split(",") if a.strip()],
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        for match in self.STRUCT_DECL.finditer(content):
            classes.append(
                ParsedClass(
                    name=match.group(1),
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        for match in self.ACTIX_ROUTE.finditer(content):
            routes.append(
                ParsedRoute(
                    path=match.group(1),
                    http_method="ACTIX",
                    handler_name="actix_handler",
                    framework="Actix",
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        for match in self.ENV_PATTERN.finditer(content):
            if match.group(1):
                env_vars.add(match.group(1))

        return ParsedSource(
            file_path=rel_path,
            language="Rust",
            imports=imports,
            classes=classes,
            functions=functions,
            routes=routes,
            env_vars=sorted(list(env_vars)),
            syntax_valid=True,
        )
