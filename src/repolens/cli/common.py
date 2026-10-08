"""Shared CLI helpers."""

from repolens.analysis.orchestrator import AnalysisOrchestrator, AnalysisResult
from repolens.utils.logging import error_console


def run_analysis_with_progress(orchestrator: AnalysisOrchestrator) -> AnalysisResult:
    """Run repository analysis with live progress on the terminal."""
    with error_console.status("Starting repository analysis...", spinner="dots") as status:
        return orchestrator.analyze(progress_callback=status.update)
