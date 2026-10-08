"""Codebase Q&A, explain, and find CLI commands."""

from pathlib import Path
from typing import Annotated, Any, Optional
import typer

from repolens.agents.architecture import ArchitectureAgent
from repolens.agents.question import QuestionAgent
from repolens.ai.factory import get_llm_provider
from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.analysis.ranking import CodebaseRanker
from repolens.cli.common import run_analysis_with_progress
from repolens.config.loader import load_config
from repolens.utils.logging import console, setup_logging


def _unwrap(val: Any) -> Any:
    if val is not None and type(val).__name__ in {"OptionInfo", "ArgumentInfo"}:
        return getattr(val, "default", None)
    return val


def run_ask_cmd(
    question: Annotated[str, typer.Argument(help="Question to ask about the codebase")],
    path: Annotated[Path, typer.Option("--path", "-p", help="Path to repository")] = Path("."),
    no_ai: Annotated[bool, typer.Option("--no-ai", help="Run deterministic search and analysis without AI provider")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
) -> None:
    """Ask questions about how components work or where to make code changes."""
    question = str(_unwrap(question) or "")
    path = _unwrap(path) or Path(".")
    no_ai = bool(_unwrap(no_ai))
    verbose = bool(_unwrap(verbose))

    setup_logging(verbose=verbose)
    config = load_config(root_dir=path, cli_overrides={"no_ai": no_ai})

    orchestrator = AnalysisOrchestrator(config)
    result = run_analysis_with_progress(orchestrator)

    ranker = CodebaseRanker(
        inventory=orchestrator.inventory,
        parsed_sources=orchestrator.parsed_sources,
        max_file_size=config.analysis.max_file_size,
    )
    llm = get_llm_provider(config.ai)

    agent = QuestionAgent(analysis_result=result, ranker=ranker, llm=llm)
    response = agent.ask(question)

    console.print(f"\n[bold cyan]Question:[/bold cyan] {question}\n")
    console.print(response.answer)
    console.print("")


def run_explain_cmd(
    topic: Annotated[Optional[str], typer.Argument(help="Specific feature or topic to explain (default: full architecture)")] = None,
    path: Annotated[Path, typer.Option("--path", "-p", help="Path to repository")] = Path("."),
    no_ai: Annotated[bool, typer.Option("--no-ai", help="Deterministic static mode")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
) -> None:
    """Explain codebase architecture, component flows, or specific features."""
    topic = _unwrap(topic)
    path = _unwrap(path) or Path(".")
    no_ai = bool(_unwrap(no_ai))
    verbose = bool(_unwrap(verbose))

    setup_logging(verbose=verbose)
    config = load_config(root_dir=path, cli_overrides={"no_ai": no_ai})

    orchestrator = AnalysisOrchestrator(config)
    result = run_analysis_with_progress(orchestrator)

    llm = get_llm_provider(config.ai)
    agent = ArchitectureAgent(analysis_result=result, llm=llm)
    response = agent.explain(focus_area=topic)

    console.print(f"\n[bold cyan]Architecture Intelligence:[/bold cyan]\n")
    console.print(response.answer)
    console.print("")


def run_find_cmd(
    term: Annotated[str, typer.Argument(help="Search query (file, module, endpoint, symbol)")],
    path: Annotated[Path, typer.Option("--path", "-p", help="Path to repository")] = Path("."),
    top_k: Annotated[int, typer.Option("--top", "-k", help="Number of results to return")] = 10,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
) -> None:
    """Ranked codebase search across files, routes, classes, and functions."""
    term = str(_unwrap(term) or "")
    path = _unwrap(path) or Path(".")
    top_k = int(_unwrap(top_k) or 10)
    verbose = bool(_unwrap(verbose))

    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)

    orchestrator = AnalysisOrchestrator(config)
    run_analysis_with_progress(orchestrator)

    ranker = CodebaseRanker(
        inventory=orchestrator.inventory,
        parsed_sources=orchestrator.parsed_sources,
        max_file_size=config.analysis.max_file_size,
    )
    hits = ranker.search(query=term, top_k=top_k)

    console.print(f"\n[bold cyan]Codebase Search Results for:[/bold cyan] '{term}'\n")
    if not hits:
        console.print("[dim]No matching files or symbols found.[/dim]\n")
        return

    for idx, hit in enumerate(hits, 1):
        console.print(f"[bold]{idx}. {hit.file_path}:{hit.line_number}[/bold] [dim](Score: {int(hit.relevance_score)})[/dim]")
        console.print(f"   [yellow]Reason:[/yellow] {hit.matched_reason}")
        if hit.snippet:
            console.print(f"   [dim]Snippet:[/dim] {hit.snippet}")
        console.print("")
