"""Filesystem scanner and file inventory collector."""

import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from repolens.scanner.ignore import IgnoreFilter
from repolens.scanner.metadata import DirectoryMetadata, FileMetadata, RepositoryInventory
from repolens.utils.filesystem import (
    count_lines,
    is_binary_file,
    normalize_relpath,
    read_file_safely,
)

# Known manifest filenames
MANIFEST_NAMES: Set[str] = {
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb",
    "requirements.txt", "pyproject.toml", "pipfile", "poetry.lock", "setup.py", "setup.cfg",
    "go.mod", "go.sum",
    "cargo.toml", "cargo.lock",
    "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle",
    "gemfile", "gemfile.lock",
    "composer.json", "composer.lock",
    "mix.exs", "mix.lock",
    "cmakelists.txt", "makefile",
    "dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yaml", "compose.yml",
}

# Known config filenames / extensions
CONFIG_NAMES: Set[str] = {
    ".env.example", ".env.sample", ".env.template", ".env.local.example",
    "tsconfig.json", "jsconfig.json", "vite.config.js", "vite.config.ts",
    "next.config.js", "next.config.mjs", "next.config.ts",
    "webpack.config.js", "rollup.config.js", "tailwind.config.js", "tailwind.config.ts",
    "babel.config.json", ".eslintrc.json", ".eslintrc.js", "eslint.config.js",
    "ruff.toml", ".flake8", "tox.ini", "pytest.ini", ".prettierrc",
    "repolens.toml",
}

# Known test directory names and file patterns
TEST_DIRS: Set[str] = {"tests", "test", "__tests__", "spec", "specs", "e2e"}


def is_test_file(rel_path: str, filename: str) -> bool:
    name_lower = filename.lower()
    path_parts = set(rel_path.lower().split("/"))

    if bool(path_parts & TEST_DIRS):
        return True
    if name_lower.startswith("test_") or name_lower.endswith("_test.py") or name_lower.endswith(".test.js") or name_lower.endswith(".spec.js") or name_lower.endswith(".test.ts") or name_lower.endswith(".spec.ts") or name_lower.endswith(".test.jsx") or name_lower.endswith(".spec.jsx") or name_lower.endswith(".test.tsx") or name_lower.endswith(".spec.tsx") or name_lower.endswith("_test.go") or name_lower.endswith("test.java"):
        return True
    return False


def is_entrypoint_file(rel_path: str, filename: str) -> bool:
    name_lower = filename.lower()
    entry_names = {
        "main.py", "app.py", "server.py", "wsgi.py", "asgi.py", "manage.py",
        "index.js", "main.js", "server.js", "app.js", "index.ts", "main.ts", "server.ts", "app.ts",
        "main.jsx", "main.tsx", "app.jsx", "app.tsx",
        "main.go", "main.rs", "app.java", "main.java",
    }
    if name_lower in entry_names:
        return True
    if rel_path.startswith("cmd/") and name_lower == "main.go":
        return True
    if rel_path.startswith("src/main.") or rel_path.startswith("app/main."):
        return True
    return False


def is_doc_file(filename: str, ext: str) -> bool:
    name_lower = filename.lower()
    if ext in {".md", ".rst", ".adoc", ".txt"}:
        if name_lower.startswith("readme") or name_lower.startswith("architecture") or name_lower.startswith("contributing") or name_lower.startswith("api") or name_lower.startswith("setup") or name_lower.startswith("changelog") or name_lower.startswith("license"):
            return True
    return False


def compute_file_hash(path: Path) -> str:
    """Compute sha256 hash of file content."""
    try:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]
    except Exception:
        return ""


def scan_directory_tree(
    root: Path,
    ignore_filter: IgnoreFilter,
    max_file_size: int = 500_000,
    max_depth: int = 15,
) -> RepositoryInventory:
    """Scan directory recursively and build RepositoryInventory."""
    inventory = RepositoryInventory(root=root, name=root.name)

    # Check git presence
    git_dir = root / ".git"
    if git_dir.exists() and git_dir.is_dir():
        inventory.has_git = True
        head_file = git_dir / "HEAD"
        if head_file.exists():
            try:
                head_content = head_file.read_text(encoding="utf-8").strip()
                if head_content.startswith("ref: refs/heads/"):
                    inventory.git_branch = head_content.replace("ref: refs/heads/", "")
            except Exception:
                pass

    total_files = 0
    total_dirs = 0
    total_lines = 0
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)

        # Depth check
        try:
            rel_dir = current_dir.relative_to(root)
            depth = len(rel_dir.parts)
        except ValueError:
            depth = 0

        if depth > max_depth:
            dirnames.clear()
            continue

        # Prune ignored directories in-place for performance
        dirnames[:] = [d for d in dirnames if not ignore_filter.is_ignored(current_dir / d)]

        rel_dir_str = normalize_relpath(current_dir, root) if current_dir != root else "."
        dir_meta = DirectoryMetadata(
            path=rel_dir_str,
            full_path=current_dir,
            file_count=0,
            dir_count=len(dirnames),
            total_size_bytes=0,
        )

        for filename in filenames:
            file_path = current_dir / filename
            if ignore_filter.is_ignored(file_path):
                continue

            try:
                stat = file_path.stat()
                file_size = stat.st_size
            except (OSError, PermissionError):
                continue

            rel_file_str = normalize_relpath(file_path, root)
            ext = file_path.suffix.lower()
            binary = is_binary_file(file_path)
            lines = 0 if binary else count_lines(file_path)
            fhash = compute_file_hash(file_path)

            filename_lower = filename.lower()
            is_manifest = filename_lower in MANIFEST_NAMES
            is_cfg = filename_lower in CONFIG_NAMES or ext in {".env", ".toml", ".yaml", ".yml", ".ini", ".cfg"}
            is_doc = is_doc_file(filename, ext)
            is_test = is_test_file(rel_file_str, filename)
            is_entry = is_entrypoint_file(rel_file_str, filename)

            file_meta = FileMetadata(
                path=rel_file_str,
                full_path=file_path,
                filename=filename,
                extension=ext,
                size_bytes=file_size,
                lines_count=lines,
                content_hash=fhash,
                is_binary=binary,
                is_test=is_test,
                is_config=is_cfg,
                is_documentation=is_doc,
                is_entrypoint_candidate=is_entry,
            )

            inventory.files[rel_file_str] = file_meta
            dir_meta.file_count += 1
            dir_meta.total_size_bytes += file_size

            total_files += 1
            total_lines += lines
            total_size += file_size

            if is_manifest:
                inventory.manifest_files.append(rel_file_str)
            if is_cfg:
                inventory.config_files.append(rel_file_str)
            if is_doc:
                inventory.doc_files.append(rel_file_str)
            if is_test:
                inventory.test_files.append(rel_file_str)

        inventory.directories[rel_dir_str] = dir_meta
        total_dirs += 1

    inventory.total_files = total_files
    inventory.total_directories = total_dirs
    inventory.total_lines = total_lines
    inventory.total_size_bytes = total_size

    return inventory
