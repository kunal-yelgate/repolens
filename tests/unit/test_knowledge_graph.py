"""Unit tests for knowledge graph and documentation generation."""

from pathlib import Path
from repolens.config.models import RepoLensConfig
from repolens.documentation.generator import DocumentationGenerator
from repolens.graph.builder import KnowledgeGraphBuilder
from repolens.graph.dependency import DependencyGraphAnalyzer
from repolens.graph.models import EntityType, GraphNode
from repolens.parsers.base import ParsedImport, ParsedSource
from repolens.scanner.metadata import FileMetadata, RepositoryInventory


def test_knowledge_graph_and_cycles(tmp_path: Path) -> None:
    inv = RepositoryInventory(root=tmp_path, name="test_repo")
    f1 = FileMetadata(
        path="module_a.py", full_path=tmp_path / "module_a.py", filename="module_a.py",
        extension=".py", size_bytes=100, lines_count=10, content_hash="h1",
    )
    f2 = FileMetadata(
        path="module_b.py", full_path=tmp_path / "module_b.py", filename="module_b.py",
        extension=".py", size_bytes=100, lines_count=10, content_hash="h2",
    )
    inv.files = {"module_a.py": f1, "module_b.py": f2}

    p1 = ParsedSource(file_path="module_a.py", language="Python", imports=[ParsedImport(module="module_b")])
    p2 = ParsedSource(file_path="module_b.py", language="Python", imports=[ParsedImport(module="module_a")])

    kg = KnowledgeGraphBuilder().build(inv, {"module_a.py": p1, "module_b.py": p2})
    cycles = kg.find_circular_dependencies()
    assert len(cycles) > 0

    analyzer = DependencyGraphAnalyzer(kg)
    deps = analyzer.get_file_dependencies("module_a.py")
    assert "module_b.py" in deps["imports"]


def test_documentation_generator(tmp_path: Path) -> None:
    from repolens.analysis.orchestrator import AnalysisOrchestrator
    cfg = RepoLensConfig()
    cfg.project.root = tmp_path
    (tmp_path / "main.py").write_text("print('test')", encoding="utf-8")

    orchestrator = AnalysisOrchestrator(cfg)
    result = orchestrator.analyze()

    doc_gen = DocumentationGenerator(output_dir=tmp_path / "docs")
    generated = doc_gen.generate_all(result)

    assert "REPOLENS.md" in generated
    assert "ARCHITECTURE.md" in generated
    assert "SETUP.md" in generated
    assert "TESTING.md" in generated
    assert "API.md" in generated
    assert "ONBOARDING.md" in generated

    for p in generated.values():
        assert p.exists()
        assert len(p.read_text(encoding="utf-8")) > 50
