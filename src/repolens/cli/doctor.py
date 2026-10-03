"""Doctor command to diagnose local environment, runtimes, dependencies, and configuration."""

import os
import shutil
import sys
from pathlib import Path
from typing import Annotated, Any, Optional
import typer
from rich.panel import Panel

from repolens.ai.factory import get_llm_provider
from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.loader import load_config
from repolens.utils.filesystem import read_file_safely
from repolens.utils.logging import console, setup_logging
from repolens.utils.subprocess import SafeCommandRunner


def _unwrap(val: Any) -> Any:
    if val is not None and type(val).__name__ in {"OptionInfo", "ArgumentInfo"}:
        return getattr(val, "default", None)
    return val


def run_doctor(
    path: Annotated[Path, typer.Option("--path", "-p", help="Path to repository")] = Path("."),
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
) -> None:
    """Diagnose repository environment, dependencies, toolchains, and configurations."""
    path = _unwrap(path) or Path(".")
    verbose = bool(_unwrap(verbose))

    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)
    runner = SafeCommandRunner()

    console.print("\n[bold cyan]RepoLens Doctor[/bold cyan]\n")

    # 1. Check Python
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"[green]✓[/green] Python {py_ver}")

    # 2. Check Git
    git_path = shutil.which("git")
    if git_path:
        console.print("[green]✓[/green] Git")
    else:
        console.print("[yellow]⚠[/yellow] Git not found in PATH")

    # 3. Check Node & npm
    node_path = shutil.which("node")
    if node_path:
        res = runner.run("node -v")
        console.print(f"[green]✓[/green] Node.js ({res.stdout.strip()})")
    else:
        console.print("[dim]○ Node.js not detected[/dim]")

    npm_path = shutil.which("npm")
    if npm_path:
        console.print("[green]✓[/green] npm")

    # 4. Check Docker
    docker_path = shutil.which("docker")
    if docker_path:
        console.print("[green]✓[/green] Docker")
    else:
        console.print("[yellow]⚠[/yellow] Docker not installed")

    # 5. Check Project analysis & environment variables
    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    console.print("[green]✓[/green] Project structure analyzed")

    # Check .env configuration vs .env.example
    env_example = config.project.root / ".env.example"
    env_local = config.project.root / ".env"

    missing_vars = []
    if env_example.exists():
        example_content = read_file_safely(env_example) or ""
        local_content = read_file_safely(env_local) or "" if env_local.exists() else ""
        for line in example_content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                var_name = line.split("=", 1)[0].strip()
                if var_name:
                    in_local = var_name in local_content
                    in_sys = var_name in os.environ
                    if not in_local and not in_sys:
                        missing_vars.append(var_name)

    if missing_vars:
        console.print(f"[red]✗[/red] Missing required environment variables: {', '.join(missing_vars[:5])}")
    else:
        console.print("[green]✓[/green] Environment variables configuration")

    # 6. Check AI Provider
    provider = get_llm_provider(config.ai)
    if provider.is_available() and provider.__class__.__name__ != "NullLLMProvider":
        console.print(f"[green]✓[/green] AI Provider ({config.ai.provider} / {config.ai.model or 'default'})")
    else:
        console.print(f"[dim]○ AI Provider: Running in deterministic static mode ({config.ai.provider})[/dim]")

    # Recommendations
    if missing_vars:
        console.print("\n[bold yellow]Recommendations:[/bold yellow]")
        console.print(f"• Create `.env` from `.env.example` and configure: {', '.join(missing_vars)}")

    console.print("")
