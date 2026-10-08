"""Unit tests for file scanner and repository metadata."""

from pathlib import Path
from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.models import RepoLensConfig
from repolens.scanner.files import is_entrypoint_file, is_test_file, scan_directory_tree
from repolens.scanner.ignore import IgnoreFilter
from repolens.scanner.repository import RepositoryScanner


def test_is_test_file() -> None:
    assert is_test_file("tests/test_auth.py", "test_auth.py")
    assert is_test_file("backend/app/auth_test.go", "auth_test.go")
    assert is_test_file("frontend/src/Button.test.tsx", "Button.test.tsx")
    assert is_test_file("frontend/src/Button.spec.jsx", "Button.spec.jsx")
    assert not is_test_file("src/main.py", "main.py")
    assert not is_test_file("frontend/src/Button.tsx", "Button.tsx")


def test_is_entrypoint_file() -> None:
    assert is_entrypoint_file("main.py", "main.py")
    assert is_entrypoint_file("app.py", "app.py")
    assert is_entrypoint_file("cmd/server/main.go", "main.go")
    assert is_entrypoint_file("frontend/src/main.jsx", "main.jsx")
    assert not is_entrypoint_file("utils/helpers.py", "helpers.py")


def test_scan_directory_tree(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_x(): pass", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"name": "demo"}', encoding="utf-8")

    ignore_filter = IgnoreFilter(root=tmp_path)
    inv = scan_directory_tree(root=tmp_path, ignore_filter=ignore_filter)

    assert inv.total_files == 3
    assert "src/main.py" in inv.files
    assert "package.json" in inv.manifest_files
    assert "tests/test_main.py" in inv.test_files


def test_large_files_are_inventoried_without_reading_content(tmp_path: Path) -> None:
    small_file = tmp_path / "small.py"
    small_file.write_text("print('small')\n", encoding="utf-8")
    large_file = tmp_path / "large.py"
    large_file.write_text("print('large')\n" * 20, encoding="utf-8")

    progress_updates = []
    inventory = scan_directory_tree(
        root=tmp_path,
        ignore_filter=IgnoreFilter(root=tmp_path),
        max_file_size=20,
        progress_callback=progress_updates.append,
    )

    assert inventory.total_files == 2
    assert inventory.skipped_large_files == 1
    assert inventory.files["large.py"].lines_count == 0
    assert inventory.files["large.py"].content_hash == ""
    assert inventory.files["small.py"].lines_count == 1
    assert inventory.files["small.py"].content_hash
    assert progress_updates[-1] == "Scanned 2 files in 1 directories"


def test_analysis_skips_large_files_and_reports_them(tmp_path: Path) -> None:
    (tmp_path / "small.py").write_text("def small():\n    return 1\n", encoding="utf-8")
    (tmp_path / "large.py").write_text(
        "def large():\n    return 2\n" * 20, encoding="utf-8"
    )
    config = RepoLensConfig()
    config.project.root = tmp_path
    config.analysis.max_file_size = 32
    config.cache_dir = tmp_path / ".repolens"

    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    assert result.repository.skipped_large_files == 1
    assert "small.py" in orchestrator.parsed_sources
    assert "large.py" not in orchestrator.parsed_sources
