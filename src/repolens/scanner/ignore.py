"""Ignore pattern management (.gitignore, .repolensignore, defaults)."""

import fnmatch
from pathlib import Path
from typing import List, Optional, Set

DEFAULT_IGNORE_PATTERNS: Set[str] = {
    # Version control
    ".git",
    ".svn",
    ".hg",
    ".bzr",
    # Dependencies
    "node_modules",
    "bower_components",
    "jspm_packages",
    "vendor",
    # Virtual environments & Python cache
    "venv",
    ".venv",
    "env",
    ".env_custom",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".eggs",
    "*.egg-info",
    # Build & distribution
    "dist",
    "build",
    "target",
    "out",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".output",
    ".turbo",
    ".cache",
    ".parcel-cache",
    # Coverage & reports
    "coverage",
    ".nyc_output",
    "htmlcov",
    ".coverage",
    "*.lcov",
    # IDE & Editors
    ".idea",
    ".vscode",
    ".vs",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
    # RepoLens cache
    ".repolens",
    # Logs & temp
    "*.log",
    "logs",
    "tmp",
    "temp",
}


class IgnoreFilter:
    """Manages ignore rules from defaults, .gitignore, and .repolensignore."""

    def __init__(
        self,
        root: Path,
        custom_includes: Optional[List[str]] = None,
        custom_excludes: Optional[List[str]] = None,
    ) -> None:
        self.root = root.resolve()
        self.patterns: List[str] = list(DEFAULT_IGNORE_PATTERNS)
        self.includes: List[str] = custom_includes or []

        if custom_excludes:
            self.patterns.extend(custom_excludes)

        self._load_ignore_file(self.root / ".gitignore")
        self._load_ignore_file(self.root / ".repolensignore")

    def _load_ignore_file(self, file_path: Path) -> None:
        if file_path.exists() and file_path.is_file():
            try:
                for line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    cleaned = line.strip()
                    if cleaned and not cleaned.startswith("#"):
                        # Normalize pattern
                        if cleaned.endswith("/"):
                            cleaned = cleaned[:-1]
                        if cleaned.startswith("/"):
                            cleaned = cleaned[1:]
                        if cleaned:
                            self.patterns.append(cleaned)
            except Exception:
                pass

    def is_ignored(self, path: Path) -> bool:
        """Check if a given path is ignored."""
        try:
            rel = path.relative_to(self.root)
            rel_str = rel.as_posix()
            parts = rel.parts
        except ValueError:
            rel_str = path.as_posix()
            parts = path.parts

        # Custom explicit includes override ignores
        for inc in self.includes:
            if fnmatch.fnmatch(rel_str, inc) or any(fnmatch.fnmatch(p, inc) for p in parts):
                return False

        # Check parts and relative path against ignore patterns
        for pattern in self.patterns:
            # Check individual directory / filename parts
            for part in parts:
                if part == pattern or fnmatch.fnmatch(part, pattern):
                    return True
            # Check full relative path match
            if fnmatch.fnmatch(rel_str, pattern) or fnmatch.fnmatch(rel_str, f"*/{pattern}") or fnmatch.fnmatch(rel_str, f"{pattern}/*"):
                return True

        return False
