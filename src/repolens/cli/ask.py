"""Codebase Q&A, explain, and find CLI commands."""

from pathlib import Path
from typing import Optional
import typer

from repolens.agents.architecture import ArchitectureAgent
from repolens.agents.question import QuestionAgent
from repolens.ai.factory import get_llm_provider
from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.analysis.ranking import CodebaseRanker
from repolens.config.loader import load_config
from repolens.utils.logging import console, setup_logging


def run_ask_cmd(
    question: str = typer.Argument(..., help="Question to ask about the codebase"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Run deterministic search and analysis without AI provider"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Ask questions about how components work or where to make code changes."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path, cli_overrides={"no_ai": no_ai})

    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    ranker = CodebaseRanker(
        inventory=orchestrator.scanner.scan(),
        parsed_sources={},
    )
    llm = get_llm_provider(config.ai)

    agent = QuestionAgent(analysis_result=result, ranker=ranker, llm=llm)
    response = agent.ask(question)

    console.print(f"\n[bold cyan]Question:[/bold cyan] {question}\n")
    console.print(response.answer)
    console.print("")


def run_explain_cmd(
    topic: Optional[str] = typer.Argument(None, help="Specific feature or topic to explain (default: full architecture)"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Deterministic static mode"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Explain codebase architecture, component flows, or specific features."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path, cli_overrides={"no_ai": no_ai})

    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    llm = get_llm_provider(config.ai)
    agent = ArchitectureAgent(analysis_result=result, llm=llm)
    response = agent.explain(focus_area=topic)

    console.print(f"\n[bold cyan]Architecture Intelligence:[/bold cyan]\n")
    console.print(response.answer)
    console.print("")


def run_find_cmd(
    term: str = typer.Argument(..., help="Search query (file, module, endpoint, symbol)"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    top_k: int = typer.Option(10, "--top", "-k", help="Number of results to return"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Ranked codebase search across files, routes, classes, and functions."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)

    orchestrator = AnalysisOrchestrator(config)
    result = orchestrator.analyze()

    inventory = orchestrator.scanner.scan()
    ranker = CodebaseRanker(inventory=inventory, parsed_sources={})
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
