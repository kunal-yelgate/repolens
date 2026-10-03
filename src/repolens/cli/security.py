"""Security, API, Git, Config, and Onboarding CLI commands."""

from pathlib import Path
from typing import Optional
import typer
from rich.table import Table

from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.loader import load_config
from repolens.documentation.generator import DocumentationGenerator
from repolens.utils.filesystem import safe_write_text
from repolens.utils.logging import console, setup_logging


def run_security_cmd(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run static security checks and secret leak detection."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)

    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    console.print("\n[bold cyan]RepoLens Security Scan[/bold cyan]\n")

    if not result.security_findings:
        console.print("[bold green]✓ No obvious secrets or critical security violations detected.[/bold green]\n")
        return

    table = Table(title="Security Observations")
    table.add_column("Severity", style="bold red")
    table.add_column("Finding", style="white")
    table.add_column("Location", style="cyan")
    table.add_column("Observation & Recommendation", style="yellow")

    for f in result.security_findings:
        table.add_row(
            f.severity,
            f.title,
            f"{f.file_path}:{f.line_number}",
            f"{f.observation}\n[dim]-> {f.recommendation}[/dim]",
        )

    console.print(table)
    console.print("")


def run_api_cmd(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """List detected API routes, methods, frameworks, and auth requirements."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)

    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    console.print("\n[bold cyan]Discovered API Endpoints[/bold cyan]\n")

    if not result.endpoints:
        console.print("[dim]No HTTP API endpoints detected.[/dim]\n")
        return

    table = Table(title=f"API Endpoints ({len(result.endpoints)} Total)")
    table.add_column("Method", style="bold green")
    table.add_column("Path", style="bold white")
    table.add_column("Framework", style="cyan")
    table.add_column("Handler", style="magenta")
    table.add_column("Auth Required", style="yellow")
    table.add_column("Source", style="dim")

    for ep in result.endpoints:
        auth_str = "Yes" if ep.auth_required else "No"
        table.add_row(
            ep.http_method,
            ep.path,
            ep.framework,
            ep.handler_name,
            auth_str,
            f"{ep.file_path}:{ep.line_number}",
        )

    console.print(table)
    console.print("")


def run_git_cmd(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Analyze Git repository history and active development areas."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)
    target_root = config.project.root.resolve()

    console.print("\n[bold cyan]Git Repository Intelligence[/bold cyan]\n")

    from repolens.utils.subprocess import SafeCommandRunner
    runner = SafeCommandRunner()

    res_branch = runner.run("git rev-parse --abbrev-ref HEAD", cwd=target_root)
    if not res_branch.success:
        console.print("[dim]Directory is not a Git repository or Git is unavailable.[/dim]\n")
        return

    branch = res_branch.stdout.strip()
    console.print(f"[bold]Active Branch:[/bold] `{branch}`")

    # Recent commits
    res_log = runner.run("git log -n 5 --pretty=format:%h%x09%an%x09%ad%x09%s --date=short", cwd=target_root)
    if res_log.success and res_log.stdout.strip():
        console.print("\n[bold]Recent Commits:[/bold]")
        for line in res_log.stdout.splitlines()[:5]:
            parts = line.split("\t")
            if len(parts) >= 4:
                console.print(f"  • [yellow]{parts[0]}[/yellow] [dim]{parts[2]}[/dim] - {parts[3]} ([cyan]{parts[1]}[/cyan])")

    # Top modified files recently
    res_active = runner.run("git log --name-only --oneline -n 20", cwd=target_root)
    if res_active.success:
        file_counts = {}
        for line in res_active.stdout.splitlines():
            cleaned = line.strip()
            if cleaned and " " not in cleaned and "/" in cleaned:
                file_counts[cleaned] = file_counts.get(cleaned, 0) + 1
        if file_counts:
            console.print("\n[bold]Active Development Hotspots:[/bold]")
            for f, cnt in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                console.print(f"  • {f} ({cnt} recent commits)")

    console.print("")


def run_config_cmd(
    provider: Optional[str] = typer.Option(None, "--provider", help="Set default AI provider (ollama, openai, etc.)"),
    model: Optional[str] = typer.Option(None, "--model", help="Set default model name"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
) -> None:
    """View or configure RepoLens settings."""
    config_file = path / "repolens.toml"

    if provider or model:
        content = f"""[project]
name = "{path.resolve().name}"

[analysis]
max_file_size = 500000
max_depth = 15

[ai]
provider = "{provider or 'none'}"
model = "{model or ''}"

[security]
scan_secrets = true
"""
        safe_write_text(config_file, content)
        console.print(f"[bold green]✓ Configuration saved to {config_file}[/bold green]\n")
    else:
        cfg = load_config(root_dir=path)
        console.print("\n[bold cyan]Current Configuration:[/bold cyan]")
        console.print(f"Project: {cfg.project.name}")
        console.print(f"AI Provider: {cfg.ai.provider}")
        console.print(f"Model: {cfg.ai.model or '(default)'}")
        console.print(f"Max File Size: {cfg.analysis.max_file_size} bytes")
        console.print(f"Max Depth: {cfg.analysis.max_depth}\n")


def run_onboarding_cmd(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Generate developer onboarding guide (ONBOARDING.md)."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)

    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    doc_out = output or config.project.root.resolve()
    gen = DocumentationGenerator(doc_out)
    files = gen.generate_all(result)

    console.print(f"\n[bold green]✓ Developer Onboarding Guide created:[/bold green] {files.get('ONBOARDING.md')}\n")
