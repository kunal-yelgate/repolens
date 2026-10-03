"""Analyze command implementation."""

import json
from pathlib import Path
from typing import Annotated, Any, Optional
import typer
from rich.panel import Panel
from rich.table import Table

from repolens.ai.factory import get_llm_provider
from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.loader import load_config
from repolens.documentation.generator import DocumentationGenerator
from repolens.utils.logging import console, setup_logging


def _unwrap(val: Any) -> Any:
    if val is not None and type(val).__name__ == "OptionInfo":
        return getattr(val, "default", None)
    return val


def run_analyze(
    path: Annotated[Path, typer.Option("--path", "-p", help="Path to repository")] = Path("."),
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Directory to save generated docs")] = None,
    format_opt: Annotated[str, typer.Option("--format", "-f", help="Output format: terminal, json, markdown")] = "terminal",
    no_ai: Annotated[bool, typer.Option("--no-ai", help="Disable AI reasoning and run deterministic static analysis only")] = False,
    llm: Annotated[Optional[str], typer.Option("--llm", help="AI provider (ollama, openai, anthropic, gemini, groq)")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="Model name to use")] = None,
    depth: Annotated[int, typer.Option("--depth", "-d", help="Maximum directory traversal depth")] = 15,
    incremental: Annotated[bool, typer.Option("--incremental", "-i", help="Enable incremental caching")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output results as JSON")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show verbose debug logs")] = False,
    force: Annotated[bool, typer.Option("--force", help="Force re-generation")] = False,
) -> None:
    """Analyze a software repository and generate architectural intelligence & documentation."""
    path = _unwrap(path) or Path(".")
    output = _unwrap(output)
    format_opt = _unwrap(format_opt) or "terminal"
    no_ai = bool(_unwrap(no_ai))
    llm = _unwrap(llm)
    model = _unwrap(model)
    depth = int(_unwrap(depth) or 15)
    incremental = bool(_unwrap(incremental))
    json_output = bool(_unwrap(json_output))
    verbose = bool(_unwrap(verbose))
    force = bool(_unwrap(force))

    setup_logging(verbose=verbose)

    cli_overrides = {
        "output_dir": output,
        "format": "json" if json_output else format_opt,
        "no_ai": no_ai,
        "provider": llm,
        "model": model,
        "depth": depth,
        "incremental": incremental,
    }

    config = load_config(root_dir=path, cli_overrides=cli_overrides)
    target_root = config.project.root.resolve()

    if not json_output and format_opt != "json":
        console.print("[brand]RepoLens[/brand]\n[dim]Autonomous Codebase Intelligence Agent[/dim]\n")
        console.print(f"[bold]Repository:[/bold] {target_root}\n")
        console.print("[dim]Scanning repository...[/dim]\n")

    # Run analysis orchestrator
    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    # Generate documentation files – always inside .repolens/docs/ for project cleanliness
    doc_out_dir = Path(output) if output else (target_root / ".repolens" / "docs")
    doc_gen = DocumentationGenerator(doc_out_dir)
    generated_files = doc_gen.generate_all(result)

    # Handle JSON output
    if json_output or format_opt == "json":
        json_data = {
            "project": result.repository.name,
            "root": result.repository.root,
            "languages": result.repository.languages,
            "frameworks": result.repository.frameworks,
            "project_types": result.repository.project_types,
            "architecture": [a.model_dump() for a in result.architecture],
            "entry_points": [e.model_dump() for e in result.entry_points],
            "database": [d.model_dump() for d in result.database],
            "endpoints": [ep.model_dump() for ep in result.endpoints],
            "environment_variables": [ev.model_dump() for ev in result.environment_variables],
            "testing": [t.model_dump() for t in result.testing],
            "commands": result.commands.model_dump(),
            "cicd": result.cicd.model_dump(),
            "monorepo": result.monorepo.model_dump(),
            "security_findings": [s.model_dump() for s in result.security_findings],
            "architectural_concerns": [c.model_dump() for c in result.architectural_concerns],
            "generated_files": [str(p) for p in generated_files.values()],
        }
        console.print(json.dumps(json_data, indent=2))
        return

    # Render beautiful Rich Terminal Output
    console.print("[green]✓[/green] Repository detected")
    console.print(f"[green]✓[/green] Languages detected: {', '.join(result.repository.languages.keys())}")
    console.print(f"[green]✓[/green] Frameworks detected: {', '.join(result.repository.frameworks) if result.repository.frameworks else 'None'}")
    console.print(f"[green]✓[/green] Dependencies analyzed ({result.repository.total_files} files)")
    console.print(f"[green]✓[/green] Entry points detected ({len(result.entry_points)} entry points)")
    console.print(f"[green]✓[/green] Configuration analyzed ({len(result.environment_variables)} env vars)")
    console.print(f"[green]✓[/green] Architecture reconstructed ({', '.join([a.architecture for a in result.architecture])})")
    console.print(f"[green]✓[/green] Tests detected ({len(result.testing)} suites)")
    console.print(f"[green]✓[/green] Documentation generated ({', '.join(generated_files.keys())})\n")

    # Codebase Summary Card
    console.print("=" * 50)
    console.print("[bold cyan]CODEBASE SUMMARY[/bold cyan]")
    console.print("=" * 50)
    console.print(f"[bold]Project:[/bold] {result.repository.name}")
    console.print(f"[bold]Type:[/bold] {', '.join(result.repository.project_types)}")
    console.print(f"[bold]Languages:[/bold] {', '.join([f'{k} ({v}%)' for k, v in result.repository.languages.items()])}")
    if result.repository.frameworks:
        console.print(f"[bold]Frameworks:[/bold] {', '.join(result.repository.frameworks)}")

    if result.architecture:
        console.print(f"[bold]Architecture:[/bold] {result.architecture[0].architecture}")

    if result.database:
        db = result.database[0]
        db_desc = db.technology + (f" ({db.orm})" if db.orm else "")
        console.print(f"[bold]Database:[/bold] {db_desc}")

    if result.entry_points:
        console.print("[bold]Main Entry Points:[/bold]")
        for ep in result.entry_points[:3]:
            console.print(f"  • {ep.file} ({ep.reason})")

    if result.testing:
        console.print(f"[bold]Tests:[/bold] {result.testing[0].framework} ({', '.join(result.testing[0].test_dirs)})")

    # Commands Card
    console.print("\n" + "=" * 50)
    console.print("[bold cyan]PROJECT COMMANDS[/bold cyan]")
    console.print("=" * 50)
    if result.commands.install:
        console.print("[bold yellow]Install:[/bold yellow]")
        for label, cmd in result.commands.install.items():
            console.print(f"  [dim]{label}:[/dim]\n  {cmd}")

    if result.commands.dev:
        console.print("\n[bold yellow]Development:[/bold yellow]")
        for label, cmd in result.commands.dev.items():
            console.print(f"  [dim]{label}:[/dim]\n  {cmd}")

    if result.commands.test:
        console.print("\n[bold yellow]Testing:[/bold yellow]")
        for label, cmd in result.commands.test.items():
            console.print(f"  [dim]{label}:[/dim]\n  {cmd}")

    # Architecture Diagram Card
    console.print("\n" + "=" * 50)
    console.print("[bold cyan]ARCHITECTURE[/bold cyan]")
    console.print("=" * 50)
    console.print(result.ascii_architecture)

    # Generated Docs List
    console.print("\n" + "=" * 50)
    console.print("[bold green]Generated Documentation:[/bold green]")
    for doc_name, doc_path in generated_files.items():
        console.print(f"  [green]✓[/green] {doc_name} -> [dim]{doc_path}[/dim]")
    console.print("=" * 50 + "\n")
