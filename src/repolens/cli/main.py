"""Main CLI entry point for RepoLens."""

from pathlib import Path
from typing import Optional
import typer
from rich.panel import Panel

from repolens.cli.analyze import run_analyze
from repolens.cli.ask import run_ask_cmd, run_explain_cmd, run_find_cmd
from repolens.cli.doctor import run_doctor
from repolens.cli.graph import run_graph_cmd
from repolens.cli.security import (
    run_api_cmd,
    run_config_cmd,
    run_git_cmd,
    run_onboarding_cmd,
    run_security_cmd,
)
from repolens.cli.setup import run_setup_cmd
from repolens.cli.test import run_test_cmd
from repolens.utils.filesystem import safe_write_text
from repolens.utils.logging import console

app = typer.Typer(
    name="repolens",
    help="RepoLens — Autonomous Codebase Analysis & Architecture Agent.",
    no_args_is_help=False,
    add_completion=False,
)

# Register subcommands
app.command(name="analyze", help="Analyze repository architecture, dependencies, and generate docs.")(run_analyze)
app.command(name="doctor", help="Check local runtimes, dependencies, configuration, and tools.")(run_doctor)
app.command(name="explain", help="Explain complete architecture or specific modules.")(run_explain_cmd)
app.command(name="ask", help="Ask questions about how components work or where to change code.")(run_ask_cmd)
app.command(name="find", help="Ranked codebase search across files and symbols.")(run_find_cmd)
app.command(name="graph", help="Visualize module and dependency relationships.")(run_graph_cmd)
app.command(name="test", help="Safely run tests, analyze failures, and suggest fixes.")(run_test_cmd)
app.command(name="setup", help="Interactive setup assistant to configure dependencies.")(run_setup_cmd)
app.command(name="security", help="Scan for hardcoded secrets and security risks.")(run_security_cmd)
app.command(name="api", help="List discovered REST & web API routes.")(run_api_cmd)
app.command(name="git", help="Analyze Git commit history and hotspots.")(run_git_cmd)
app.command(name="config", help="View or update RepoLens configuration.")(run_config_cmd)
app.command(name="onboarding", help="Generate developer onboarding guide (ONBOARDING.md).")(run_onboarding_cmd)


from typing import Annotated, Any, Optional

def _unwrap(val: Any) -> Any:
    if val is not None and type(val).__name__ in {"OptionInfo", "ArgumentInfo"}:
        return getattr(val, "default", None)
    return val


@app.command(name="init", help="Initialize repolens.toml and .repolensignore in the current repository.")
def run_init(
    path: Annotated[Path, typer.Option("--path", "-p", help="Directory to initialize")] = Path("."),
) -> None:
    path = _unwrap(path) or Path(".")
    target_dir = path.resolve()
    cfg_file = target_dir / "repolens.toml"
    ignore_file = target_dir / ".repolensignore"

    cfg_content = f"""[project]
name = "{target_dir.name}"

[analysis]
max_file_size = 500000
max_depth = 15

[ai]
provider = "none"

[security]
scan_secrets = true

[output]
format = "markdown"
"""
    ignore_content = """# RepoLens ignore list
node_modules/
.venv/
venv/
dist/
build/
coverage/
.next/
.cache/
"""
    safe_write_text(cfg_file, cfg_content)
    safe_write_text(ignore_file, ignore_content)
    console.print(f"\n[bold green]✓ Initialized RepoLens in {target_dir}[/bold green]")
    console.print("  • Created repolens.toml")
    console.print("  • Created .repolensignore\n")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[Optional[bool], typer.Option("--version", "-V", help="Show version")] = None,
) -> None:
    """RepoLens — Autonomous Codebase Intelligence Agent."""
    version = bool(_unwrap(version))
    if version:
        from repolens import __version__
        console.print(f"RepoLens version: {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        # Interactive prompt mode
        console.print("\n[brand]RepoLens[/brand] — Autonomous Codebase Intelligence Agent\n")
        console.print("What would you like to do?\n")
        console.print("1. Analyze repository (`repolens analyze`)")
        console.print("2. Explain architecture (`repolens explain`)")
        console.print("3. Ask a question (`repolens ask <question>`)")
        console.print("4. Find code (`repolens find <term>`)")
        console.print("5. Run tests (`repolens test`)")
        console.print("6. Check setup (`repolens doctor`)")
        console.print("7. Security scan (`repolens security`)")
        console.print("8. Generate documentation (`repolens analyze --format markdown`)\n")

        choice = typer.prompt("Select an option (1-8)", default="1")
        if choice == "1":
            run_analyze(path=Path("."))
        elif choice == "2":
            run_explain_cmd(topic=None, path=Path("."))
        elif choice == "3":
            q = typer.prompt("Enter your question")
            run_ask_cmd(question=q, path=Path("."))
        elif choice == "4":
            t = typer.prompt("Enter search term")
            run_find_cmd(term=t, path=Path("."))
        elif choice == "5":
            run_test_cmd(path=Path("."))
        elif choice == "6":
            run_doctor(path=Path("."))
        elif choice == "7":
            run_security_cmd(path=Path("."))
        elif choice == "8":
            run_analyze(path=Path("."), format_opt="markdown")


if __name__ == "__main__":
    app()
