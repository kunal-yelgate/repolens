"""Autonomous test validation runner and failure analysis."""

import re
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from repolens.utils.logging import log_info, log_warning
from repolens.utils.subprocess import CommandResult, SafeCommandRunner
from repolens.validation.safety import is_safe_command


class TestFailureItem(BaseModel):
    test_name: str
    cause: str
    suggested_action: str


class ValidationReport(BaseModel):
    command: str
    passed: bool
    total_passed: int = 0
    total_failed: int = 0
    failures: List[TestFailureItem] = Field(default_factory=list)
    raw_stdout: str = ""
    raw_stderr: str = ""


class ValidationRunner:
    """Safely executes test suites, analyzes failures, and suggests actionable fixes."""

    def __init__(self, cwd: Path) -> None:
        self.cwd = cwd
        self.runner = SafeCommandRunner()

    def run_tests(self, test_cmd: str, timeout: int = 120) -> ValidationReport:
        safe, reason = is_safe_command(test_cmd)
        if not safe:
            return ValidationReport(
                command=test_cmd,
                passed=False,
                raw_stderr=reason,
            )

        log_info(f"Running test suite: {test_cmd}")
        result = self.runner.run(test_cmd, cwd=self.cwd, timeout=timeout)

        report = self._analyze_output(test_cmd, result)
        return report

    def _analyze_output(self, test_cmd: str, res: CommandResult) -> ValidationReport:
        output = (res.stdout + "\n" + res.stderr).strip()

        # Parse pytest output
        # e.g.: "3 passed, 1 failed in 0.5s" or "FAILED tests/test_auth.py::test_login"
        pytest_summary_match = re.search(r'(\d+)\s+passed', output)
        passed_count = int(pytest_summary_match.group(1)) if pytest_summary_match else (1 if res.success else 0)

        failed_summary_match = re.search(r'(\d+)\s+failed', output)
        failed_count = int(failed_summary_match.group(1)) if failed_summary_match else (0 if res.success else 1)

        failures: List[TestFailureItem] = []

        # Find specific failed test cases
        failed_tests = re.findall(r'FAILED\s+([^\s]+)', output)
        for t in failed_tests:
            cause = "Test assertion or unhandled exception"
            action = "Inspect test implementation and debug error trace"

            if "DATABASE_URL" in output:
                cause = "DATABASE_URL environment variable is missing"
                action = "Create .env from .env.example and configure DATABASE_URL."
            elif "connection refused" in output.lower() or "could not connect" in output.lower():
                cause = "Required external service (database or server) is unavailable"
                action = "Ensure database service (PostgreSQL/Redis/MySQL) is running locally or via docker-compose."
            elif "ModuleNotFoundError" in output or "Cannot find module" in output:
                missing_mod = re.search(r"No module named ['\"]([^'\"]+)['\"]", output)
                mod_name = missing_mod.group(1) if missing_mod else "dependency"
                cause = f"Missing dependency: {mod_name}"
                action = f"Run dependency install command (e.g., pip install {mod_name} or npm install)."

            failures.append(
                TestFailureItem(
                    test_name=t,
                    cause=cause,
                    suggested_action=action,
                )
            )

        if not failures and not res.success:
            failures.append(
                TestFailureItem(
                    test_name="Suite Execution",
                    cause="Command failed with non-zero exit code",
                    suggested_action="Check test output for syntax or runtime errors.",
                )
            )

        return ValidationReport(
            command=test_cmd,
            passed=res.success,
            total_passed=passed_count,
            total_failed=failed_count,
            failures=failures,
            raw_stdout=res.stdout,
            raw_stderr=res.stderr,
        )
