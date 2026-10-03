"""Entry point detection with confidence and architectural evidence."""

import json
from pathlib import Path
from typing import Dict, List

from repolens.detectors.base import BaseDetector, EntryPointInfo
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely


class EntryPointDetector(BaseDetector):
    """Detects application entry points using AST parsing, manifest inspection, and heuristic checks."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> List[EntryPointInfo]:
        entry_points: List[EntryPointInfo] = []
        seen_files = set()

        # 1. Inspect package.json
        for rel_path, fmeta in inventory.files.items():
            if fmeta.filename.lower() == "package.json":
                content = read_file_safely(fmeta.full_path)
                if content:
                    try:
                        data = json.loads(content)
                        base_dir = str(Path(rel_path).parent.as_posix())
                        prefix = f"{base_dir}/" if base_dir != "." else ""

                        # "main" field
                        main_f = data.get("main")
                        if main_f and not main_f.startswith("http"):
                            target_rel = (prefix + main_f.lstrip("./")).replace("//", "/")
                            if target_rel in inventory.files and target_rel not in seen_files:
                                entry_points.append(
                                    EntryPointInfo(
                                        file=target_rel,
                                        type="module_entrypoint",
                                        confidence=0.90,
                                        reason="Declared as 'main' in package.json",
                                        evidence=[f"package.json: 'main': '{main_f}'"],
                                    )
                                )
                                seen_files.add(target_rel)

                        # "bin" field
                        bin_f = data.get("bin")
                        if isinstance(bin_f, str):
                            target_rel = (prefix + bin_f.lstrip("./")).replace("//", "/")
                            if target_rel in inventory.files and target_rel not in seen_files:
                                entry_points.append(
                                    EntryPointInfo(
                                        file=target_rel,
                                        type="cli",
                                        confidence=0.95,
                                        reason="Declared as 'bin' in package.json",
                                        evidence=[f"package.json: 'bin': '{bin_f}'"],
                                    )
                                )
                                seen_files.add(target_rel)
                        elif isinstance(bin_f, dict):
                            for bname, bpath in bin_f.items():
                                target_rel = (prefix + bpath.lstrip("./")).replace("//", "/")
                                if target_rel in inventory.files and target_rel not in seen_files:
                                    entry_points.append(
                                        EntryPointInfo(
                                            file=target_rel,
                                            type="cli",
                                            confidence=0.95,
                                            reason=f"Declared as CLI binary '{bname}' in package.json",
                                            evidence=[f"package.json: 'bin.{bname}': '{bpath}'"],
                                        )
                                    )
                                    seen_files.add(target_rel)
                    except Exception:
                        pass

            # 2. Inspect pyproject.toml scripts
            elif fmeta.filename.lower() == "pyproject.toml":
                content = read_file_safely(fmeta.full_path)
                if content and "[project.scripts]" in content:
                    for line in content.split("[project.scripts]")[1].split("\n\n")[0].splitlines():
                        if "=" in line and not line.strip().startswith("#"):
                            cli_name, mod_target = line.split("=", 1)
                            entry_points.append(
                                EntryPointInfo(
                                    file=rel_path,
                                    type="cli",
                                    confidence=0.95,
                                    reason=f"Declared console script '{cli_name.strip()}' in pyproject.toml",
                                    evidence=[f"{cli_name.strip()} = {mod_target.strip()}"],
                                )
                            )

        # 3. Inspect inventory files and parsed sources for framework app instances and main functions
        target_files = set(parsed_sources.keys()) | {p for p, f in inventory.files.items() if f.is_entrypoint_candidate or f.extension in {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs"}}
        for rel_path in target_files:
            if rel_path in seen_files or rel_path not in inventory.files:
                continue

            parsed = parsed_sources.get(rel_path)
            content = read_file_safely(inventory.files[rel_path].full_path) or ""
            fname_lower = inventory.files[rel_path].filename.lower()

            # FastAPI / Flask app initialization
            if "FastAPI(" in content or "Flask(" in content:
                fw = "FastAPI" if "FastAPI(" in content else "Flask"
                entry_points.append(
                    EntryPointInfo(
                        file=rel_path,
                        type="web_application",
                        confidence=0.95,
                        reason=f"Instantiates {fw} application",
                        evidence=[f"Found {fw}(...) instance in {rel_path}"],
                    )
                )
                seen_files.add(rel_path)

            # Express app initialization
            elif "express()" in content or "fastify()" in content:
                fw = "Express" if "express()" in content else "Fastify"
                entry_points.append(
                    EntryPointInfo(
                        file=rel_path,
                        type="web_application",
                        confidence=0.90,
                        reason=f"Instantiates {fw} server",
                        evidence=[f"Found {fw}() invocation in {rel_path}"],
                    )
                )
                seen_files.add(rel_path)

            # React/Vite/Next entrypoints
            elif fname_lower in {"main.jsx", "main.tsx", "index.jsx", "index.tsx", "app.jsx", "app.tsx", "layout.tsx", "layout.jsx"}:
                if "createRoot" in content or "ReactDOM.render" in content or "export default function" in content or "createBrowserRouter" in content:
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="frontend_entrypoint",
                            confidence=0.92,
                            reason="React / Web client UI root mount",
                            evidence=[f"Root renderer found in {rel_path}"],
                        )
                    )
                    seen_files.add(rel_path)

            # Go main package
            elif (parsed and parsed.language == "Go") or rel_path.endswith(".go"):
                if (rel_path == "main.go" or rel_path.startswith("cmd/")) and ("func main()" in content or (parsed and any(fn.name == "main" for fn in parsed.functions))):
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="application",
                            confidence=0.95,
                            reason="Go main package with func main()",
                            evidence=["package main with func main()"],
                        )
                    )
                    seen_files.add(rel_path)

            # Rust main
            elif (parsed and parsed.language == "Rust") or rel_path.endswith(".rs"):
                if rel_path.endswith("main.rs") and ("fn main()" in content or (parsed and any(fn.name == "main" for fn in parsed.functions))):
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="application",
                            confidence=0.95,
                            reason="Rust binary entry point fn main()",
                            evidence=["fn main()"],
                        )
                    )
                    seen_files.add(rel_path)

            # Java / Kotlin main
            elif rel_path.endswith((".java", ".kt")):
                if "public static void main" in content or "@SpringBootApplication" in content or "fun main(" in content:
                    reason_str = "Spring Boot Application" if "@SpringBootApplication" in content else "Java/Kotlin main method"
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="application",
                            confidence=0.95,
                            reason=reason_str,
                            evidence=[f"Found entry point in {rel_path}"],
                        )
                    )
                    seen_files.add(rel_path)

            # C / C++ main
            elif rel_path.endswith((".c", ".cpp", ".cc", ".cxx")):
                if "int main(" in content or "void main(" in content:
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="application",
                            confidence=0.95,
                            reason="C/C++ main entry function",
                            evidence=[f"main() found in {rel_path}"],
                        )
                    )
                    seen_files.add(rel_path)

            # C# main
            elif rel_path.endswith(".cs"):
                if "static void Main(" in content or "static async Task Main(" in content or fname_lower == "program.cs":
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="application",
                            confidence=0.95,
                            reason="C# Main entry point",
                            evidence=[f"Main method found in {rel_path}"],
                        )
                    )
                    seen_files.add(rel_path)

            # PHP entrypoints
            elif rel_path.endswith(".php"):
                if fname_lower in {"index.php", "artisan", "server.php"}:
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="web_application" if fname_lower != "artisan" else "cli",
                            confidence=0.90,
                            reason=f"PHP entrypoint script ({fname_lower})",
                            evidence=[f"PHP script {rel_path}"],
                        )
                    )
                    seen_files.add(rel_path)

            # Ruby entrypoints
            elif rel_path.endswith(".rb") or fname_lower == "config.ru":
                if fname_lower in {"config.ru", "environment.rb", "application.rb"} or rel_path.startswith("bin/"):
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="application",
                            confidence=0.90,
                            reason=f"Ruby / Rails application entry ({fname_lower})",
                            evidence=[f"Ruby entry {rel_path}"],
                        )
                    )
                    seen_files.add(rel_path)

            # Dart / Flutter main
            elif rel_path.endswith(".dart"):
                if "void main()" in content or "void main(" in content:
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="mobile_application" if "runApp" in content else "application",
                            confidence=0.95,
                            reason="Dart / Flutter main function",
                            evidence=[f"main() in {rel_path}"],
                        )
                    )
                    seen_files.add(rel_path)

            # Python executable script
            elif (parsed and parsed.language == "Python") or rel_path.endswith(".py"):
                if '__name__ == "__main__"' in content.replace("'", '"'):
                    entry_points.append(
                        EntryPointInfo(
                            file=rel_path,
                            type="executable_script",
                            confidence=0.85,
                            reason="Python executable block (if __name__ == '__main__':)",
                            evidence=[f"__main__ block in {rel_path}"],
                        )
                    )
                    seen_files.add(rel_path)


        # Sort by confidence descending
        return sorted(entry_points, key=lambda x: x.confidence, reverse=True)
