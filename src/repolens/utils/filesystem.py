"""Cross-platform filesystem utilities for RepoLens."""

import os
from pathlib import Path
from typing import Iterator, List, Optional, Set, Tuple


BINARY_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svgz", ".webp", ".bmp",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar", ".bz2", ".xz",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".pyc", ".pyd", ".o", ".a",
    ".mp3", ".wav", ".ogg", ".mp4", ".mov", ".avi", ".mkv",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".sqlite", ".db", ".parquet", ".npy", ".pkl", ".pt", ".onnx", ".h5",
}


def is_binary_file(path: Path) -> bool:
    """Check if a file is binary based on extension and first byte check."""
    ext = path.suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return True
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except (OSError, IOError, PermissionError):
        return True
    return False


def read_file_safely(
    path: Path,
    max_size: int = 1_000_000,
    encoding_fallback: str = "latin-1",
) -> Optional[str]:
    """Read a text file safely with size limit and fallback encoding."""
    try:
        if not path.is_file():
            return None
        file_size = path.stat().st_size
        if file_size > max_size:
            return None
        if is_binary_file(path):
            return None

        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                return path.read_text(encoding=encoding_fallback)
            except Exception:
                return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError, PermissionError):
        return None


def count_lines(path: Path) -> int:
    """Count non-empty lines in a file safely."""
    content = read_file_safely(path)
    if content is None:
        return 0
    return sum(1 for line in content.splitlines() if line.strip())


def normalize_relpath(path: Path, root: Path) -> str:
    """Return forward-slash relative path string from root."""
    try:
        rel = path.relative_to(root)
        return rel.as_posix()
    except ValueError:
        return path.as_posix()


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write_text(path: Path, content: str, encoding: str = "utf-8") -> bool:
    """Safely write content to a file, ensuring parent directory exists."""
    try:
        ensure_dir(path.parent)
        path.write_text(content, encoding=encoding)
        return True
    except (OSError, IOError, PermissionError):
        return False
