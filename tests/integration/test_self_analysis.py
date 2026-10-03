"""Self-analysis test verifying RepoLens can analyze its own repository."""

from pathlib import Path
from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.models import RepoLensConfig


def test_repolens_analyzes_itself() -> None:
    root_dir = Path(__file__).parent.parent.parent.resolve()
    cfg = RepoLensConfig()
    cfg.project.root = root_dir

    orchestrator = AnalysisOrchestrator(cfg)
    result = orchestrator.analyze()

    assert result.repository.name in {"repolens", "repolens"}
    assert "Python" in result.repository.languages
    assert result.repository.total_files > 15
    assert len(result.entry_points) >= 1
    assert any("cli" in ep.reason.lower() or "pyproject" in ep.reason.lower() for ep in result.entry_points)
    assert any(a.architecture == "Modular CLI Application" for a in result.architecture)
    assert len(result.testing) >= 1
    assert result.testing[0].framework == "pytest"
