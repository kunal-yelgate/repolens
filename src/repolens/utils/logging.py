"""Logging and console display utilities for RepoLens."""

import logging
import sys
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "highlight": "bold magenta",
        "dim": "dim white",
        "brand": "bold cyan",
    }
)

console = Console(theme=custom_theme, legacy_windows=False)
error_console = Console(theme=custom_theme, stderr=True, legacy_windows=False)


logger = logging.getLogger("repolens")


def setup_logging(verbose: bool = False) -> None:
    """Setup structured Rich logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    logger.handlers.clear()

    handler = RichHandler(
        console=error_console,
        show_time=verbose,
        show_path=verbose,
        markup=True,
        rich_tracebacks=True,
    )
    handler.setLevel(level)
    logger.addHandler(handler)


def log_debug(msg: str) -> None:
    logger.debug(msg)


def log_info(msg: str) -> None:
    logger.info(msg)


def log_warning(msg: str) -> None:
    logger.warning(msg)


def log_error(msg: str) -> None:
    logger.error(msg)
