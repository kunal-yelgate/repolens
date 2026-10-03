"""Test framework and test suite detector."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from repolens.detectors.base import BaseDetector, TestFrameworkInfo
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely


class TestingDetector(BaseDetector):
    """Detects testing frameworks, suites, and execution commands."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> List[TestFrameworkInfo]:
        results: List[TestFrameworkInfo] = []

        test_files = inventory.test_files
        test_dirs = sorted(
            list({str(Path(f).parent.as_posix()) for f in test_files if "/" in f})
        )

        has_python = any(f.endswith(".py") for f in test_files) or any(f.endswith(".py") for f in inventory.files)
        has_js_ts = any(f.endswith((".js", ".ts", ".jsx", ".tsx")) for f in test_files) or any(f.endswith((".js", ".ts")) for f in inventory.files)
        has_go = any(f.endswith("_test.go") for f in test_files)
        has_rust = any(f.endswith(".rs") for f in inventory.files)

        # Check Python test frameworks
        if has_python:
            has_pytest_cfg = any(
                f in inventory.files for f in ["pytest.ini", "setup.cfg", "pyproject.toml", "tox.ini"]
            )
            results.append(
                TestFrameworkInfo(
                    framework="pytest",
                    test_dirs=[d for d in test_dirs if "test" in d.lower() or "tests" in d.lower()] or ["tests/"],
                    test_files_count=sum(1 for f in test_files if f.endswith(".py")),
                    run_all_command="pytest",
                    run_single_command_template="pytest {test_file}",
                )
            )

        # Check JS/TS test frameworks in package.json
        if has_js_ts:
            framework_name = "Jest"
            run_cmd = "npm test"
            for rel_path, fmeta in inventory.files.items():
                if fmeta.filename.lower() == "package.json":
                    content = read_file_safely(fmeta.full_path)
                    if content:
                        try:
                            data = json.loads(content)
                            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                            scripts = data.get("scripts", {})

                            if "vitest" in deps or "vitest" in scripts.get("test", ""):
                                framework_name = "Vitest"
                                run_cmd = "npx vitest run"
                            elif "jest" in deps or "jest" in scripts.get("test", ""):
                                framework_name = "Jest"
                                run_cmd = "npm test"
                            elif "mocha" in deps:
                                framework_name = "Mocha"
                                run_cmd = "npx mocha"
                            elif "playwright" in deps:
                                framework_name = "Playwright"
                                run_cmd = "npx playwright test"
                            elif "cypress" in deps:
                                framework_name = "Cypress"
                                run_cmd = "npx cypress run"
                        except Exception:
                            pass

            results.append(
                TestFrameworkInfo(
                    framework=framework_name,
                    test_dirs=[d for d in test_dirs if not d.endswith(".py")] or ["tests/"],
                    test_files_count=sum(1 for f in test_files if f.endswith((".js", ".ts", ".jsx", ".tsx"))),
                    run_all_command=run_cmd,
                    run_single_command_template=f"{run_cmd} {{test_file}}",
                )
            )

        # Check Go test
        if has_go:
            results.append(
                TestFrameworkInfo(
                    framework="Go test",
                    test_dirs=[d for d in test_dirs if any(f.endswith("_test.go") for f in test_files)],
                    test_files_count=sum(1 for f in test_files if f.endswith("_test.go")),
                    run_all_command="go test ./...",
                    run_single_command_template="go test -v {test_file}",
                )
            )

        # Check Rust cargo test
        if has_rust and "Cargo.toml" in inventory.files:
            results.append(
                TestFrameworkInfo(
                    framework="Cargo test",
                    test_dirs=["tests/"] if "tests" in inventory.directories else ["src/"],
                    test_files_count=sum(1 for f in test_files if f.endswith(".rs")),
                    run_all_command="cargo test",
                    run_single_command_template="cargo test --test {test_name}",
                )
            )

        return results
