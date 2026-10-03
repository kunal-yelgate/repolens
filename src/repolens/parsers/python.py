"""Python AST parser using standard library `ast`."""

import ast
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


class PythonParser(BaseParser):
    """Parses Python source files using AST."""

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".py", ".pyw"}

    def parse(self, file_path: Path, content: str, rel_path: str) -> ParsedSource:
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return ParsedSource(
                file_path=rel_path,
                language="Python",
                syntax_valid=False,
                error_message=f"SyntaxError at line {e.lineno}: {e.msg}",
            )
        except Exception as e:
            return ParsedSource(
                file_path=rel_path,
                language="Python",
                syntax_valid=False,
                error_message=str(e),
            )

        imports: List[ParsedImport] = []
        classes: List[ParsedClass] = []
        functions: List[ParsedFunction] = []
        routes: List[ParsedRoute] = []
        env_vars: Set[str] = set()
        db_models: List[str] = []

        # Visitor to extract details
        for node in ast.walk(tree):
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ParsedImport(
                            module=alias.name,
                            imported_names=[],
                            alias=alias.asname,
                            is_relative=False,
                            line_number=node.lineno,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                mod_name = ("." * node.level) + (node.module or "")
                names = [n.name for n in node.names]
                imports.append(
                    ParsedImport(
                        module=mod_name,
                        imported_names=names,
                        is_relative=node.level > 0,
                        line_number=node.lineno,
                    )
                )

            # os.getenv / os.environ calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"getenv", "get"}:
                        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                            env_vars.add(node.args[0].value)
            elif isinstance(node, ast.Subscript):
                # os.environ["KEY"]
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                    if isinstance(node.value, ast.Attribute) and node.value.attr == "environ":
                        env_vars.add(node.slice.value)

        # Iterate top-level & class-level definitions
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = self._parse_function(node)
                functions.append(fn)
                route = self._check_route(node, "fastapi_or_flask")
                if route:
                    routes.append(route)

            elif isinstance(node, ast.ClassDef):
                cls_obj = self._parse_class(node)
                classes.append(cls_obj)

                # Check if it's a database model (Base, Model, DeclarativeBase, Document)
                db_base_names = {"Base", "Model", "DeclarativeBase", "Document", "SQLModel", "db.Model"}
                if any(b in db_base_names or b.endswith("Model") or b.endswith("Base") for b in cls_obj.base_classes):
                    db_models.append(cls_obj.name)

        return ParsedSource(
            file_path=rel_path,
            language="Python",
            imports=imports,
            classes=classes,
            functions=functions,
            routes=routes,
            env_vars=sorted(list(env_vars)),
            db_models=db_models,
            syntax_valid=True,
        )

    def _parse_function(self, node: ast.AST) -> ParsedFunction:
        is_async = isinstance(node, ast.AsyncFunctionDef)
        name = getattr(node, "name", "unknown")
        args: List[str] = []
        if hasattr(node, "args"):
            args = [a.arg for a in node.args.args if a.arg != "self" and a.arg != "cls"]

        decorators = [self._decorator_to_str(d) for d in getattr(node, "decorator_list", [])]
        docstring = ast.get_docstring(node)

        # Collect function calls inside body
        calls: List[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)

        return ParsedFunction(
            name=name,
            args=args,
            is_async=is_async,
            decorators=decorators,
            line_number=getattr(node, "lineno", 1),
            docstring=docstring,
            calls=calls[:20],
        )

    def _parse_class(self, node: ast.ClassDef) -> ParsedClass:
        base_classes: List[str] = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                base_classes.append(b.id)
            elif isinstance(b, ast.Attribute):
                val_id = getattr(b.value, "id", "")
                base_classes.append(f"{val_id}.{b.attr}")

        methods: List[ParsedFunction] = []
        fields: List[str] = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._parse_function(item))
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    fields.append(item.target.id)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        fields.append(target.id)

        return ParsedClass(
            name=node.name,
            base_classes=base_classes,
            methods=methods,
            fields=fields,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
        )

    def _decorator_to_str(self, dec: ast.AST) -> str:
        if isinstance(dec, ast.Name):
            return dec.id
        elif isinstance(dec, ast.Attribute):
            val_id = getattr(dec.value, "id", "")
            return f"{val_id}.{dec.attr}"
        elif isinstance(dec, ast.Call):
            return self._decorator_to_str(dec.func)
        return ""

    def _check_route(self, node: ast.AST, framework_hint: str) -> Optional[ParsedRoute]:
        for dec in getattr(node, "decorator_list", []):
            if isinstance(dec, ast.Call):
                func_repr = self._decorator_to_str(dec.func)
                method = None
                framework = "unknown"

                # FastAPI style: @app.get("/users"), @router.post("/items")
                for http_m in ["get", "post", "put", "delete", "patch", "options", "head"]:
                    if func_repr.endswith(f".{http_m}"):
                        method = http_m.upper()
                        framework = "FastAPI"
                        break

                # Flask style: @app.route("/path", methods=["POST"])
                if func_repr.endswith(".route"):
                    framework = "Flask"
                    method = "GET"
                    for kw in dec.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                            methods_list = [
                                elt.value for elt in kw.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                            ]
                            if methods_list:
                                method = "/".join(methods_list)

                if method and dec.args:
                    first_arg = dec.args[0]
                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                        path = first_arg.value
                        fn_name = getattr(node, "name", "unknown")
                        # Check auth requirement in decorator / params
                        auth_required = any("auth" in d.lower() or "current_user" in d.lower() or "depends" in d.lower() for d in [func_repr] + [a.arg for a in getattr(node, "args", ast.arguments()).args if hasattr(a, "arg")])
                        return ParsedRoute(
                            path=path,
                            http_method=method,
                            handler_name=fn_name,
                            framework=framework,
                            line_number=getattr(node, "lineno", 1),
                            auth_required=auth_required,
                        )
        return None
