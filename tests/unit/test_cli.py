"""Unit tests for CLI commands and OptionInfo safety."""

import json
from pathlib import Path
from repolens.cli.analyze import run_analyze
from repolens.cli.doctor import run_doctor
from repolens.cli.ask import run_explain_cmd, run_find_cmd
from repolens.cli.security import run_security_cmd, run_api_cmd


def test_run_analyze_direct_call(tmp_path: Path) -> None:
    """Verify run_analyze can be invoked directly as a function without OptionInfo errors."""
    run_analyze(path=tmp_path)


def test_json_output_reports_large_files_without_log_noise(
    tmp_path: Path, capsys
) -> None:
    (tmp_path / "small.py").write_text("print('small')\n", encoding="utf-8")
    (tmp_path / "large.py").write_text("print('large')\n" * 20, encoding="utf-8")

    run_analyze(
        path=tmp_path,
        json_output=True,
        no_ai=True,
        max_file_size=20,
    )

    result = json.loads(capsys.readouterr().out)
    assert result["total_files"] == 2
    assert result["skipped_large_files"] == 1


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
