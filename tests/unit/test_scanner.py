"""Unit tests for file scanner and repository metadata."""

from pathlib import Path
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
