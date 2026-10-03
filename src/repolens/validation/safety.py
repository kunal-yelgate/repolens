"""Command safety rules and guardrails."""

import re
from typing import List, Tuple

DANGEROUS_COMMAND_PATTERNS = [
    re.compile(r'\brm\s+-[rf]{1,2}\s+[/~]'),
    re.compile(r'\bformat\s+[c-z]:', re.IGNORECASE),
    re.compile(r'\bdel\s+/[fqs]\s+[c-z]:\\', re.IGNORECASE),
    re.compile(r'\bdd\s+if='),
    re.compile(r'\bmkfs\b'),
    re.compile(r'\bshutdown\b'),
    re.compile(r'\breboot\b'),
    re.compile(r'\bcurl\s+.*\|\s*sh\b'),
    re.compile(r'\bwget\s+.*\|\s*sh\b'),
    re.compile(r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;:'),  # Fork bomb
]

SAFE_TEST_COMMANDS = {
    "pytest", "python -m pytest", "poetry run pytest", "pipenv run pytest",
    "npm test", "pnpm test", "yarn test", "npx vitest run", "npx jest",
    "go test ./...", "cargo test", "mvn test", "gradle test",
}


def is_safe_command(cmd: str) -> Tuple[bool, str]:
    """Check if a command is considered safe to prompt or execute."""
    for pattern in DANGEROUS_COMMAND_PATTERNS:
        if pattern.search(cmd):
            return False, f"Command contains potentially destructive or dangerous operations: '{cmd}'"
    return True, "Safe"
