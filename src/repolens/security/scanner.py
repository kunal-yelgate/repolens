"""Static security scanner and secret risk analyzer."""

from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.security.patterns import SECRET_PATTERNS, VULNERABILITY_PATTERNS
from repolens.utils.filesystem import read_file_safely


class SecurityFinding(BaseModel):
    title: str
    severity: str  # HIGH, MEDIUM, LOW, CRITICAL
    file_path: str
    line_number: int
    observation: str  # Always redacted, never exposing secret content
    recommendation: str


def redact_secret_string(value: str) -> str:
    """Redact secret string safely for display."""
    if len(value) <= 6:
        return "[REDACTED]"
    return f"{value[:3]}...[REDACTED]...{value[-2:]}"


class SecurityScanner:
    """Lightweight static security and secret leak scanner."""

    def scan(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []

        for rel_path, fmeta in inventory.files.items():
            if fmeta.is_binary:
                continue

            content = read_file_safely(fmeta.full_path)
            if not content:
                continue

            lines = content.splitlines()

            # 1. Scan for hardcoded secrets
            # Skip test fixture files or sample env files
            is_sample_env = fmeta.filename.startswith(".env.")
            for secret_type, pattern in SECRET_PATTERNS.items():
                for idx, line in enumerate(lines):
                    match = pattern.search(line)
                    if match:
                        matched_val = match.group(0)
                        # Avoid flagging common placeholders like "your_api_key_here" or dummy vars in example files
                        if is_sample_env or any(p in matched_val.lower() for p in ["placeholder", "example", "your-", "xxx", "dummy", "fake"]):
                            continue

                        redacted = redact_secret_string(matched_val)
                        findings.append(
                            SecurityFinding(
                                title=f"Potential Hardcoded Secret: {secret_type}",
                                severity="HIGH",
                                file_path=rel_path,
                                line_number=idx + 1,
                                observation=f"Found pattern matching {secret_type}: {redacted}",
                                recommendation=f"Remove the hardcoded secret from {rel_path} and load it via environment variables or a secrets manager.",
                            )
                        )

            # 2. Scan for static vulnerability patterns
            for vuln_key, vuln_info in VULNERABILITY_PATTERNS.items():
                pattern = vuln_info["pattern"]
                for idx, line in enumerate(lines):
                    if pattern.search(line):
                        findings.append(
                            SecurityFinding(
                                title=vuln_info["title"],
                                severity=vuln_info["severity"],
                                file_path=rel_path,
                                line_number=idx + 1,
                                observation=f"Matched security risk pattern in: {line.strip()[:80]}",
                                recommendation=vuln_info["recommendation"],
                            )
                        )

        return sorted(findings, key=lambda x: (x.severity != "HIGH", x.severity != "MEDIUM", x.file_path))
