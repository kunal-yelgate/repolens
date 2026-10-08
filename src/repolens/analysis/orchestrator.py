"""Main application orchestrator coordinating scanning, parsing, graph, and detection."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from repolens.analysis.context import StructuredCodebaseContext
from repolens.cache.manager import CacheManager
from repolens.config.models import RepoLensConfig
from repolens.detectors.api import APIDetector, DiscoveredEndpoint
from repolens.detectors.base import (
    ArchitecturalConcern,
    ArchitectureFinding,
    DatabaseInfo,
    EntryPointInfo,
    EnvVarInfo,
    ProjectCommandsInfo,
    TestFrameworkInfo,
)
from repolens.detectors.cicd import CICDDetector, CICDInfo, MonorepoDetector, MonorepoInfo
from repolens.detectors.commands import CommandDetector
from repolens.detectors.database import DatabaseDetector
from repolens.detectors.entrypoint import EntryPointDetector
from repolens.detectors.environment import EnvironmentDetector
from repolens.detectors.framework import FrameworkDetector
from repolens.detectors.language import LanguageDetector
from repolens.detectors.problems import ArchitecturalProblemsDetector
from repolens.detectors.project_type import ProjectTypeDetector
from repolens.detectors.testing import TestingDetector
from repolens.graph.architecture import ArchitectureDiagramGenerator
from repolens.graph.builder import KnowledgeGraphBuilder
from repolens.parsers import get_parser_for_file
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.scanner.repository import RepositoryScanner
from repolens.security.scanner import SecurityFinding, SecurityScanner
from repolens.utils.filesystem import read_file_safely
from repolens.utils.logging import log_debug, log_info


class RepositoryInfo(BaseModel):
    root: str
    name: str
    total_files: int
    total_lines: int
    total_directories: int = 0
    total_size_bytes: int = 0
    skipped_large_files: int = 0
    max_file_size: int = 500_000
    languages: Dict[str, float]
    frameworks: List[str]
    project_types: List[str]
    has_git: bool = False
    git_branch: Optional[str] = None


class AnalysisResult(BaseModel):
    repository: RepositoryInfo
    entry_points: List[EntryPointInfo] = Field(default_factory=list)
    architecture: List[ArchitectureFinding] = Field(default_factory=list)
    database: List[DatabaseInfo] = Field(default_factory=list)
    endpoints: List[DiscoveredEndpoint] = Field(default_factory=list)
    environment_variables: List[EnvVarInfo] = Field(default_factory=list)
    testing: List[TestFrameworkInfo] = Field(default_factory=list)
    commands: ProjectCommandsInfo = Field(default_factory=ProjectCommandsInfo)
    cicd: CICDInfo = Field(default_factory=lambda: CICDInfo(platform="None"))
    monorepo: MonorepoInfo = Field(default_factory=MonorepoInfo)
    security_findings: List[SecurityFinding] = Field(default_factory=list)
    architectural_concerns: List[ArchitecturalConcern] = Field(default_factory=list)
    ascii_tree: str = ""
    ascii_architecture: str = ""
    mermaid_diagram: str = ""
    structured_context: Optional[StructuredCodebaseContext] = None


class AnalysisOrchestrator:
    """Orchestrates deterministic static analysis and knowledge graph construction."""

    def __init__(self, config: RepoLensConfig) -> None:
        self.config = config
        self.scanner = RepositoryScanner(config)
        self.cache_mgr = CacheManager(config.cache_dir)
        self.inventory: RepositoryInventory
        self.parsed_sources: Dict[str, ParsedSource] = {}

    def analyze(
        self, progress_callback: Optional[Callable[[str], None]] = None
    ) -> AnalysisResult:
        log_info(f"Analyzing repository: {self.config.project.root}")

        # 1. Scan filesystem
        if progress_callback:
            progress_callback("Scanning repository files...")
        inventory = self.scanner.scan(progress_callback=progress_callback)
        self.inventory = inventory
        tree_str = self.scanner.generate_smart_tree(inventory)

        # 2. Parse source files with caching
        parsed_sources: Dict[str, ParsedSource] = {}
        analyzable_files = [
            (rel_path, fmeta)
            for rel_path, fmeta in inventory.files.items()
            if not fmeta.is_binary and fmeta.size_bytes <= self.config.analysis.max_file_size
        ]
        if progress_callback:
            progress_callback(f"Parsing source files (0/{len(analyzable_files):,})...")
        for index, (rel_path, fmeta) in enumerate(analyzable_files, start=1):
            cached = None
            if self.config.analysis.incremental:
                cached = self.cache_mgr.get_cached_parsed_source(rel_path, fmeta.content_hash)
            if cached:
                parsed_sources[rel_path] = cached
            else:
                content = read_file_safely(
                    fmeta.full_path, max_size=self.config.analysis.max_file_size
                )
                if content is not None:
                    parser = get_parser_for_file(fmeta.full_path)
                    try:
                        parsed = parser.parse(fmeta.full_path, content, rel_path)
                        parsed_sources[rel_path] = parsed
                    except Exception as e:
                        log_debug(f"Failed to parse {rel_path}: {e}")
            if progress_callback and index % 100 == 0:
                progress_callback(
                    f"Parsing source files ({index:,}/{len(analyzable_files):,})..."
                )

        # Save cache
        self.cache_mgr.save(parsed_sources, inventory)
        self.parsed_sources = parsed_sources

        # 3. Build Knowledge Graph
        if progress_callback:
            progress_callback("Building the dependency graph...")
        kg_builder = KnowledgeGraphBuilder()
        knowledge_graph = kg_builder.build(inventory, parsed_sources)
        self.knowledge_graph = knowledge_graph

        # 4. Run Detectors
        if progress_callback:
            progress_callback("Detecting frameworks, routes, tests, and configuration...")
        languages = LanguageDetector().detect(inventory, parsed_sources)
        frameworks = FrameworkDetector().detect(inventory, parsed_sources)
        project_types = ProjectTypeDetector().detect(inventory, parsed_sources)
        entry_points = EntryPointDetector().detect(inventory, parsed_sources)
        database_findings = DatabaseDetector().detect(inventory, parsed_sources)
        endpoints = APIDetector().detect(inventory, parsed_sources)
        testing_findings = TestingDetector().detect(inventory, parsed_sources)
        env_vars = EnvironmentDetector().detect(inventory, parsed_sources)
        commands = CommandDetector().detect(inventory, parsed_sources)
        cicd_info = CICDDetector().detect(inventory, parsed_sources)
        monorepo_info = MonorepoDetector().detect(inventory, parsed_sources)
        concerns = ArchitecturalProblemsDetector().detect(inventory, parsed_sources, knowledge_graph)

        # 5. Run Security Scanner if enabled
        security_findings: List[SecurityFinding] = []
        if self.config.security.scan_secrets or self.config.security.scan_vulnerabilities:
            if progress_callback:
                progress_callback("Checking source files for security findings...")
            security_findings = SecurityScanner().scan(inventory, parsed_sources)

        # 6. Infer High-Level Architecture
        frontend_fw = next((f for f in frameworks if f in {"React", "Next.js", "Vue", "Angular", "Svelte", "Vite"}), None)
        backend_fw = next((f for f in frameworks if f in {"FastAPI", "Django", "Flask", "Express", "NestJS", "Spring Boot", "Gin", "Actix Web"}), None)
        db_name = database_findings[0].technology if database_findings else None

        arch_findings: List[ArchitectureFinding] = []
        if frontend_fw and backend_fw:
            arch_findings.append(
                ArchitectureFinding(
                    architecture="Full-Stack (Client-Server / REST API)",
                    confidence=0.92,
                    evidence=[
                        f"Frontend: {frontend_fw}",
                        f"Backend API: {backend_fw}",
                        f"Database: {db_name or 'Configured persistence'}",
                    ],
                    source_dirs=[d for d in ["frontend", "backend", "client", "server", "app"] if d in inventory.directories],
                )
            )
        elif backend_fw:
            arch_findings.append(
                ArchitectureFinding(
                    architecture="Layered Backend Service",
                    confidence=0.88,
                    evidence=[f"Backend API framework: {backend_fw}"],
                    source_dirs=[d for d in ["app", "api", "routes", "services", "models"] if d in inventory.directories],
                )
            )
        elif "CLI tool" in project_types:
            arch_findings.append(
                ArchitectureFinding(
                    architecture="Modular CLI Application",
                    confidence=0.90,
                    evidence=["Command line entrypoint and CLI structure"],
                    source_dirs=[d for d in ["cli", "cmd", "bin"] if d in inventory.directories],
                )
            )
        else:
            arch_findings.append(
                ArchitectureFinding(
                    architecture="Standard Modular Architecture",
                    confidence=0.75,
                    evidence=["Structured repository source tree"],
                    source_dirs=list(inventory.directories.keys())[:5],
                )
            )

        # 7. Generate Diagrams
        ascii_arch = ArchitectureDiagramGenerator.generate_ascii(
            frontend=frontend_fw,
            api_layer=backend_fw,
            service_layer="Business Logic / Services" if any("service" in d.lower() for d in inventory.directories) else None,
            database=db_name,
        )
        mermaid_arch = ArchitectureDiagramGenerator.generate_mermaid(
            frontend=frontend_fw,
            api_layer=backend_fw,
            service_layer="Business Logic" if any("service" in d.lower() for d in inventory.directories) else None,
            database=db_name,
        )

        # 8. Extract key source snippets for structured context
        important_snippets: Dict[str, str] = {}
        for ep in entry_points[:3]:
            if ep.file in inventory.files:
                snip = read_file_safely(inventory.files[ep.file].full_path, max_size=10_000)
                if snip:
                    important_snippets[ep.file] = snip

        structured_ctx = StructuredCodebaseContext(
            project_name=inventory.name,
            total_files=inventory.total_files,
            total_lines=inventory.total_lines,
            languages=languages,
            frameworks=frameworks,
            project_types=project_types,
            entry_points=entry_points,
            database=database_findings,
            endpoints_sample=[f"{e.http_method} {e.path}" for e in endpoints[:20]],
            env_vars=[ev.name for ev in env_vars],
            test_frameworks=[t.framework for t in testing_findings],
            commands=commands,
            architecture_findings=[af.architecture for af in arch_findings],
            concerns=[c.observation for c in concerns],
            important_file_snippets=important_snippets,
        )

        repo_info = RepositoryInfo(
            root=str(self.config.project.root),
            name=inventory.name,
            total_files=inventory.total_files,
            total_lines=inventory.total_lines,
            total_directories=inventory.total_directories,
            total_size_bytes=inventory.total_size_bytes,
            skipped_large_files=inventory.skipped_large_files,
            max_file_size=self.config.analysis.max_file_size,
            languages=languages,
            frameworks=frameworks,
            project_types=project_types,
            has_git=inventory.has_git,
            git_branch=inventory.git_branch,
        )

        return AnalysisResult(
            repository=repo_info,
            entry_points=entry_points,
            architecture=arch_findings,
            database=database_findings,
            endpoints=endpoints,
            environment_variables=env_vars,
            testing=testing_findings,
            commands=commands,
            cicd=cicd_info,
            monorepo=monorepo_info,
            security_findings=security_findings,
            architectural_concerns=concerns,
            ascii_tree=tree_str,
            ascii_architecture=ascii_arch,
            mermaid_diagram=mermaid_arch,
            structured_context=structured_ctx,
        )
