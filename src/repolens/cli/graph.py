"""Dependency graph CLI command."""

from pathlib import Path
from typing import Optional
import typer

from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.loader import load_config
from repolens.graph.dependency import DependencyGraphAnalyzer
from repolens.utils.logging import console, setup_logging


def run_graph_cmd(
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Filter graph by module name"),
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="Inspect import dependencies for a specific file"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path to repository"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Visualize module relationships and source file dependencies."""
    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)

    orchestrator = AnalysisOrchestrator(config)
    inventory = orchestrator.scanner.scan()

    # Parse files to build KnowledgeGraph
    parsed_sources = {}
    for rel_path, fmeta in inventory.files.items():
        if not fmeta.is_binary:
            from repolens.parsers import get_parser_for_file
            from repolens.utils.filesystem import read_file_safely
            content = read_file_safely(fmeta.full_path)
            if content:
                parser = get_parser_for_file(fmeta.full_path)
                try:
                    parsed_sources[rel_path] = parser.parse(fmeta.full_path, content, rel_path)
                except Exception:
                    pass

    from repolens.graph.builder import KnowledgeGraphBuilder
    kg = KnowledgeGraphBuilder().build(inventory, parsed_sources)

    analyzer = DependencyGraphAnalyzer(kg)
    ascii_graph = analyzer.format_ascii_graph(file_path=file_path, module=module)

    console.print("\n[bold cyan]RepoLens Knowledge Graph[/bold cyan]\n")
    console.print(ascii_graph)
    console.print("")
