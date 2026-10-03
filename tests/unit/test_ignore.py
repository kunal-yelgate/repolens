"""Unit tests for ignore filtering."""

from pathlib import Path
from repolens.scanner.ignore import IgnoreFilter


def test_default_ignores(tmp_path: Path) -> None:
    filter_obj = IgnoreFilter(root=tmp_path)
    assert filter_obj.is_ignored(tmp_path / "node_modules" / "package.json")
    assert filter_obj.is_ignored(tmp_path / ".git" / "HEAD")
    assert filter_obj.is_ignored(tmp_path / ".venv" / "bin" / "python")
    assert filter_obj.is_ignored(tmp_path / "dist" / "bundle.js")
    assert not filter_obj.is_ignored(tmp_path / "src" / "main.py")


def test_custom_gitignore(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("secrets/\n*.tmp\ncustom_build/\n", encoding="utf-8")

    filter_obj = IgnoreFilter(root=tmp_path)
    assert filter_obj.is_ignored(tmp_path / "secrets" / "key.pem")
    assert filter_obj.is_ignored(tmp_path / "data.tmp")
    assert filter_obj.is_ignored(tmp_path / "custom_build" / "app.exe")
    assert not filter_obj.is_ignored(tmp_path / "src" / "index.js")
