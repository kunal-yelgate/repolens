"""Autonomous test validation CLI command."""

from pathlib import Path
from typing import Annotated, Any, Optional
import typer

from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.cli.common import run_analysis_with_progress
from repolens.config.loader import load_config
from repolens.utils.logging import console, setup_logging
from repolens.validation.runner import ValidationRunner


def _unwrap(val: Any) -> Any:
    if val is not None and type(val).__name__ in {"OptionInfo", "ArgumentInfo"}:
        return getattr(val, "default", None)
    return val


def run_test_cmd(
    path: Annotated[Path, typer.Option("--path", "-p", help="Path to repository")] = Path("."),
    command: Annotated[Optional[str], typer.Option("--command", "-c", help="Override test command to execute")] = None,
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 120,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
) -> None:
    """Safely execute tests, analyze failures, and suggest fixes."""
    path = _unwrap(path) or Path(".")
    command = _unwrap(command)
    timeout = int(_unwrap(timeout) or 120)
    verbose = bool(_unwrap(verbose))

    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)
    target_root = config.project.root.resolve()

    console.print("\n[bold cyan]RepoLens Test Runner[/bold cyan]\n")

    # Detect test command if not provided
    test_cmd = command
    if not test_cmd:
        orchestrator = AnalysisOrchestrator(config)
        result = run_analysis_with_progress(orchestrator)
        if result.testing:
            test_cmd = result.testing[0].run_all_command
        elif result.commands.test:
            test_cmd = next(iter(result.commands.test.values()))
        else:
            test_cmd = "pytest"

    console.print(f"[dim]Running tests with: '{test_cmd}'...[/dim]\n")

    runner = ValidationRunner(cwd=target_root)
    report = runner.run_tests(test_cmd=test_cmd, timeout=timeout)

    if report.passed:
        console.print(f"[bold green]✓ All tests passed successfully![/bold green] ({report.total_passed} passed)\n")
    else:
        console.print(f"[bold red]✗ {report.total_failed} tests failed[/bold red] ({report.total_passed} passed)\n")

        if report.failures:
            console.print("[bold yellow]Failure Analysis:[/bold yellow]")
            for idx, fail in enumerate(report.failures, 1):
                console.print(f"\n[bold]{idx}. {fail.test_name}[/bold]")
                console.print(f"   [red]Cause:[/red] {fail.cause}")
                console.print(f"   [green]Suggested Action:[/green] {fail.suggested_action}")

        if verbose or not report.failures:
            console.print("\n[dim]Captured stderr / stdout:[/dim]")
            console.print(report.raw_stderr or report.raw_stdout)
    console.print("")
