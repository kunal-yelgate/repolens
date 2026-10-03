"""Unit tests for CLI commands and OptionInfo safety."""

from pathlib import Path
from repolens.cli.analyze import run_analyze
from repolens.cli.doctor import run_doctor
from repolens.cli.ask import run_explain_cmd, run_find_cmd
from repolens.cli.security import run_security_cmd, run_api_cmd


def test_run_analyze_direct_call(tmp_path: Path) -> None:
    """Verify run_analyze can be invoked directly as a function without OptionInfo errors."""
    run_analyze(path=tmp_path)


def test_run_doctor_direct_call(tmp_path: Path) -> None:
    """Verify run_doctor can be invoked directly as a function."""
    run_doctor(path=tmp_path)


def test_run_explain_direct_call(tmp_path: Path) -> None:
    """Verify run_explain_cmd can be invoked directly as a function."""
    run_explain_cmd(path=tmp_path)


def test_run_find_direct_call(tmp_path: Path) -> None:
    """Verify run_find_cmd can be invoked directly as a function."""
    run_find_cmd(term="test", path=tmp_path)


def test_run_security_direct_call(tmp_path: Path) -> None:
    """Verify run_security_cmd can be invoked directly as a function."""
    run_security_cmd(path=tmp_path)


def test_run_api_direct_call(tmp_path: Path) -> None:
    """Verify run_api_cmd can be invoked directly as a function."""
    run_api_cmd(path=tmp_path)
