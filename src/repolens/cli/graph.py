"""Dependency graph CLI command."""

from pathlib import Path
from typing import Annotated, Any, Optional
import typer

from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.loader import load_config
from repolens.graph.builder import KnowledgeGraphBuilder
from repolens.graph.dependency import DependencyGraphAnalyzer
from repolens.parsers import get_parser_for_file
from repolens.utils.filesystem import read_file_safely
from repolens.utils.logging import console, error_console, log_debug, setup_logging


def _unwrap(val: Any) -> Any:
    if val is not None and type(val).__name__ in {"OptionInfo", "ArgumentInfo"}:
        return getattr(val, "default", None)
    return val


def run_graph_cmd(
    module: Annotated[Optional[str], typer.Option("--module", "-m", help="Filter graph by module name")] = None,
    file_path: Annotated[Optional[str], typer.Option("--file", "-f", help="Inspect import dependencies for a specific file")] = None,
    path: Annotated[Path, typer.Option("--path", "-p", help="Path to repository")] = Path("."),
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
) -> None:
    """Visualize module relationships and source file dependencies."""
    module = _unwrap(module)
    file_path = _unwrap(file_path)
    path = _unwrap(path) or Path(".")
    verbose = bool(_unwrap(verbose))

    setup_logging(verbose=verbose)
    config = load_config(root_dir=path)

    orchestrator = AnalysisOrchestrator(config)
    with error_console.status("Scanning repository files...", spinner="dots") as status:
        inventory = orchestrator.scanner.scan(progress_callback=status.update)
        parsed_sources = {}
        analyzable_files = [
            (rel_path, fmeta)
            for rel_path, fmeta in inventory.files.items()
            if not fmeta.is_binary and fmeta.size_bytes <= config.analysis.max_file_size
        ]
        for index, (rel_path, fmeta) in enumerate(analyzable_files, start=1):
            if index % 100 == 0:
                status.update(f"Parsing source files ({index:,}/{len(analyzable_files):,})...")
            content = read_file_safely(
                fmeta.full_path, max_size=config.analysis.max_file_size
            )
            if content:
                parser = get_parser_for_file(fmeta.full_path)
                try:
                    parsed_sources[rel_path] = parser.parse(
                        fmeta.full_path, content, rel_path
                    )
                except Exception as exc:
                    log_debug(f"Failed to parse {rel_path}: {exc}")
        kg = KnowledgeGraphBuilder().build(inventory, parsed_sources)

    analyzer = DependencyGraphAnalyzer(kg)
    ascii_graph = analyzer.format_ascii_graph(file_path=file_path, module=module)

    console.print("\n[bold cyan]RepoLens Knowledge Graph[/bold cyan]\n")
    console.print(ascii_graph)
    console.print("")
