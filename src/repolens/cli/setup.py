"""Autonomous setup assistant CLI command."""

import shutil
from pathlib import Path
from typing import Optional
import typer

from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.loader import load_config
from repolens.utils.logging import console, setup_logging
from repolens.utils.subprocess import SafeCommandRunner


def run_setup_cmd(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    auto_approve: bool = typer.Option(False, "--yes", "-y", help="Automatically confirm dependency installation"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Autonomous setup assistant to prepare and configure dependencies."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)
    target_root = config.project.root.resolve()

    console.print("\n[bold cyan]RepoLens Setup Assistant[/bold cyan]\n")

    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    # 1. Runtimes detection
    if "Python" in result.repository.languages:
        console.print("[green]✓[/green] Python runtime detected")
    if "JavaScript" in result.repository.languages or "TypeScript" in result.repository.languages:
        if shutil.which("node"):
            console.print("[green]✓[/green] Node.js runtime detected")
        else:
            console.print("[yellow]⚠[/yellow] Node.js runtime not installed")

    # 2. Check install commands
    install_commands = result.commands.install
    if not install_commands:
        console.print("\n[dim]No standard dependency manifest detected for automated install.[/dim]\n")
        return

    console.print("\n[bold]Detected Installation Steps:[/bold]")
    for label, cmd in install_commands.items():
        console.print(f"  • {label}: [yellow]{cmd}[/yellow]")

    console.print("")

    if not auto_approve:
        confirm = typer.confirm("Would you like RepoLens to install these dependencies now?", default=False)
        if not confirm:
            console.print("[dim]Setup cancelled. You can run the commands manually.[/dim]\n")
            return

    runner = SafeCommandRunner()
    for label, cmd in install_commands.items():
        console.print(f"\n[dim]Installing {label} dependencies ({cmd})...[/dim]")
        res = runner.run(cmd, cwd=target_root, timeout=300)
        if res.success:
            console.print(f"[bold green]✓ {label} dependencies installed successfully.[/bold green]")
        else:
            console.print(f"[bold red]✗ Failed to install {label} dependencies.[/bold red]")
            console.print(res.stderr or res.stdout)

    console.print("\n[bold green]✓ Setup process completed.[/bold green]\n")
