"""JavaScript and TypeScript source code parser."""

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


class JavaScriptParser(BaseParser):
    """Parses JavaScript and TypeScript source files."""

    # Regex patterns
    IMPORT_ES6 = re.compile(r'import\s+(?:(?:\*\s+as\s+(\w+)|([\w,\s{}]+))\s+from\s+)?[\'"]([^\'"]+)[\'"]', re.MULTILINE)
    IMPORT_CJS = re.compile(r'(?:const|let|var)\s+([\w,\s{}]+)\s*=\s*require\(\s*[\'"]([^\'"]+)[\'"]\s*\)', re.MULTILINE)
    DYNAMIC_IMPORT = re.compile(r'import\(\s*[\'"]([^\'"]+)[\'"]\s*\)', re.MULTILINE)

    FUNCTION_DECL = re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)', re.MULTILINE)
    ARROW_FUNCTION = re.compile(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*(?:=>|:)', re.MULTILINE)
    CLASS_DECL = re.compile(r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?', re.MULTILINE)

    # Express/Fastify/Next.js/NestJS API routes
    EXPRESS_ROUTE = re.compile(r'(?:app|router)\.(get|post|put|delete|patch|options|all)\s*\(\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
    NESTJS_ROUTE = re.compile(r'@(Get|Post|Put|Delete|Patch)\s*\(\s*(?:[\'"]([^\'"]*)[\'"])?\s*\)', re.IGNORECASE)

    # Environment variables
    ENV_PATTERN = re.compile(r'process\.env\.([A-Z0-9_]+)|process\.env\[[\'"]([A-Z0-9_]+)[\'"]\]|import\.meta\.env\.([A-Z0-9_]+)')

    # Database schemas/models (Prisma, Mongoose, TypeORM)
    PRISMA_MODEL = re.compile(r'model\s+(\w+)\s*\{', re.MULTILINE)
    MONGOOSE_MODEL = re.compile(r'mongoose\.model\s*\(\s*[\'"](\w+)[\'"]', re.MULTILINE)
    TYPEORM_ENTITY = re.compile(r'@Entity\s*\(\s*(?:[\'"](\w+)[\'"])?\s*\)\s*(?:export\s+)?class\s+(\w+)', re.MULTILINE)

    def can_parse(self, file_path: Path) -> bool:
        ext = file_path.suffix.lower()
        return ext in {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".prisma"}

    def parse(self, file_path: Path, content: str, rel_path: str) -> ParsedSource:
        is_ts = file_path.suffix.lower() in {".ts", ".tsx", ".mts", ".cts"}
        lang_name = "TypeScript" if is_ts else "JavaScript"
        if file_path.suffix.lower() == ".prisma":
            lang_name = "Prisma"

        imports: List[ParsedImport] = []
        classes: List[ParsedClass] = []
        functions: List[ParsedFunction] = []
        routes: List[ParsedRoute] = []
        env_vars: Set[str] = set()
        db_models: List[str] = []

        lines = content.splitlines()

        # 1. Imports
        for match in self.IMPORT_ES6.finditer(content):
            names_raw = match.group(1) or match.group(2) or ""
            module = match.group(3)
            names = [n.strip() for n in names_raw.replace("{", "").replace("}", "").split(",") if n.strip()]
            imports.append(
                ParsedImport(
                    module=module,
                    imported_names=names,
                    is_relative=module.startswith("."),
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        for match in self.IMPORT_CJS.finditer(content):
            names_raw = match.group(1)
            module = match.group(2)
            names = [n.strip() for n in names_raw.replace("{", "").replace("}", "").split(",") if n.strip()]
            imports.append(
                ParsedImport(
                    module=module,
                    imported_names=names,
                    is_relative=module.startswith("."),
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        # 2. Classes
        for match in self.CLASS_DECL.finditer(content):
            cls_name = match.group(1)
            base_cls = match.group(2)
            bases = [base_cls] if base_cls else []
            classes.append(
                ParsedClass(
                    name=cls_name,
                    base_classes=bases,
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        # 3. Functions
        for match in self.FUNCTION_DECL.finditer(content):
            fn_name = match.group(1)
            raw_args = match.group(2)
            args = [a.strip().split(":")[0].strip() for a in raw_args.split(",") if a.strip()]
            functions.append(
                ParsedFunction(
                    name=fn_name,
                    args=args,
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        for match in self.ARROW_FUNCTION.finditer(content):
            fn_name = match.group(1)
            raw_args = match.group(2)
            args = [a.strip().split(":")[0].strip() for a in raw_args.split(",") if a.strip()]
            functions.append(
                ParsedFunction(
                    name=fn_name,
                    args=args,
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        # 4. Routes
        for match in self.EXPRESS_ROUTE.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            line_no = content[: match.start()].count("\n") + 1
            auth_req = "auth" in content.lower() or "passport" in content.lower() or "jwt" in content.lower()
            routes.append(
                ParsedRoute(
                    path=route_path,
                    http_method=method,
                    handler_name="anonymous_or_middleware",
                    framework="Express",
                    line_number=line_no,
                    auth_required=auth_req,
                )
            )

        for match in self.NESTJS_ROUTE.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2) or "/"
            line_no = content[: match.start()].count("\n") + 1
            routes.append(
                ParsedRoute(
                    path=route_path,
                    http_method=method,
                    handler_name="controller_method",
                    framework="NestJS",
                    line_number=line_no,
                )
            )

        # Next.js App Router / Pages API detection by path
        if "app/api/" in rel_path or "pages/api/" in rel_path:
            # Check for HTTP method handlers export (GET, POST, etc.)
            for m in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                if f"export async function {m}" in content or f"export function {m}" in content:
                    # Infer path from file path
                    api_rel = rel_path.split("api/", 1)[1]
                    api_path = "/" + api_rel.replace("/route.ts", "").replace("/route.js", "").replace(".ts", "").replace(".js", "")
                    routes.append(
                        ParsedRoute(
                            path=f"/api{api_path}",
                            http_method=m,
                            handler_name=m,
                            framework="Next.js App Router",
                            line_number=1,
                        )
                    )

        # 5. Environment Variables
        for match in self.ENV_PATTERN.finditer(content):
            var_name = match.group(1) or match.group(2) or match.group(3)
            if var_name:
                env_vars.add(var_name)

        # 6. Database Models
        for match in self.PRISMA_MODEL.finditer(content):
            db_models.append(match.group(1))

        for match in self.MONGOOSE_MODEL.finditer(content):
            db_models.append(match.group(1))

        for match in self.TYPEORM_ENTITY.finditer(content):
            entity_name = match.group(2) or match.group(1)
            if entity_name:
                db_models.append(entity_name)

        return ParsedSource(
            file_path=rel_path,
            language=lang_name,
            imports=imports,
            classes=classes,
            functions=functions,
            routes=routes,
            env_vars=sorted(list(env_vars)),
            db_models=db_models,
            syntax_valid=True,
        )
