"""Unit tests for security scanning and secret redaction."""

from pathlib import Path
from repolens.scanner.files import scan_directory_tree
from repolens.scanner.ignore import IgnoreFilter
from repolens.security.scanner import SecurityScanner, redact_secret_string


def test_redact_secret_string() -> None:
    redacted = redact_secret_string("sk-proj-1234567890abcdef")
    assert "sk-" in redacted
    assert "1234567890" not in redacted
    assert "[REDACTED]" in redacted


def test_security_scanner_detection(tmp_path: Path) -> None:
    vuln_file = tmp_path / "app.py"
    vuln_file.write_text("""
import os
import subprocess

API_KEY = "AKIA1234567890ABCDEF"

def run_cmd(user_input):
    eval(user_input)
    subprocess.Popen(f"ls {user_input}", shell=True)
""", encoding="utf-8")

    inv = scan_directory_tree(root=tmp_path, ignore_filter=IgnoreFilter(root=tmp_path))
    findings = SecurityScanner().scan(inv, {})

    assert len(findings) >= 2
    assert any("AWS Access Key" in f.title for f in findings)
    assert any("eval()" in f.title for f in findings)
    # Ensure no plain secret exposed in finding observation
    for f in findings:
        assert "AKIA1234567890ABCDEF" not in f.observation
