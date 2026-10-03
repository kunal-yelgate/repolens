"""Utilities module for RepoLens."""

from repolens.utils.filesystem import (
    count_lines,
    ensure_dir,
    is_binary_file,
    normalize_relpath,
    read_file_safely,
    safe_write_text,
)
from repolens.utils.logging import (
    console,
    error_console,
    log_debug,
    log_error,
    log_info,
    log_warning,
    logger,
    setup_logging,
)
from repolens.utils.subprocess import (
    CommandResult,
    CommandRunner,
    SafeCommandRunner,
    default_runner,
)

__all__ = [
    "count_lines",
    "ensure_dir",
    "is_binary_file",
    "normalize_relpath",
    "read_file_safely",
    "safe_write_text",
    "console",
    "error_console",
    "logger",
    "setup_logging",
    "log_debug",
    "log_info",
    "log_warning",
    "log_error",
    "CommandResult",
    "CommandRunner",
    "SafeCommandRunner",
    "default_runner",
]
