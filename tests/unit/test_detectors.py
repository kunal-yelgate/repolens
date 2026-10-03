"""Unit tests for language, framework, database, entrypoint, and commands detectors."""

from pathlib import Path
from repolens.detectors.commands import CommandDetector
from repolens.detectors.database import DatabaseDetector
from repolens.detectors.entrypoint import EntryPointDetector
from repolens.detectors.framework import FrameworkDetector
from repolens.detectors.language import LanguageDetector
from repolens.detectors.project_type import ProjectTypeDetector
from repolens.parsers.base import ParsedSource
from repolens.scanner.files import scan_directory_tree
from repolens.scanner.ignore import IgnoreFilter


def test_framework_and_project_detection(tmp_path: Path) -> None:
    # Setup mock FastAPI backend
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    (backend_dir / "requirements.txt").write_text("fastapi==0.110.0\nuvicorn\nsqlalchemy\npsycopg2-binary\n", encoding="utf-8")
    (backend_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")

    # Setup mock React frontend
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "package.json").write_text('{"dependencies": {"react": "^18.0.0", "vite": "^5.0.0"}}', encoding="utf-8")

    ignore_filter = IgnoreFilter(root=tmp_path)
    inv = scan_directory_tree(root=tmp_path, ignore_filter=ignore_filter)

    frameworks = FrameworkDetector().detect(inv, {})
    assert "FastAPI" in frameworks
    assert "React" in frameworks
    assert "SQLAlchemy" in frameworks

    ptypes = ProjectTypeDetector().detect(inv, {})
    assert "Full-stack web application" in ptypes

    entrypoints = EntryPointDetector().detect(inv, {})
    assert any("main.py" in ep.file for ep in entrypoints)

    db_info = DatabaseDetector().detect(inv, {})
    assert any(d.technology == "PostgreSQL" for d in db_info)

    cmds = CommandDetector().detect(inv, {})
    assert "Backend" in cmds.install or "Python" in cmds.install
    assert "Frontend" in cmds.install
