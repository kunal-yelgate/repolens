"""Architectural smell and concern detector."""

from pathlib import Path
from typing import Dict, List, Set

from repolens.detectors.base import ArchitecturalConcern, BaseDetector
from repolens.graph.builder import KnowledgeGraph
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory


class ArchitecturalProblemsDetector:
    """Identifies architectural concerns based on concrete evidence."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
        knowledge_graph: KnowledgeGraph,
    ) -> List[ArchitecturalConcern]:
        concerns: List[ArchitecturalConcern] = []

        # 1. Circular Dependencies
        cycles = knowledge_graph.find_circular_dependencies()
        for cycle in cycles[:5]:
            clean_cycle = [c.replace("file:", "") for c in cycle]
            cycle_str = " -> ".join(clean_cycle) + " -> " + clean_cycle[0]
            concerns.append(
                ArchitecturalConcern(
                    title="Circular Dependency Detected",
                    category="circular_dependency",
                    file=clean_cycle[0],
                    observation=f"Cycle: {cycle_str}",
                    confidence=0.95,
                    suggested_action="Refactor shared types or functions into a separate utility or base module.",
                )
            )

        # 2. Very Large Files (God Files)
        for rel_path, fmeta in inventory.files.items():
            if fmeta.is_binary or fmeta.is_test or fmeta.is_documentation:
                continue
            if fmeta.lines_count > 800:
                parsed = parsed_sources.get(rel_path)
                has_routes = bool(parsed and parsed.routes)
                has_models = bool(parsed and parsed.db_models)
                has_classes = bool(parsed and len(parsed.classes) > 5)

                mixed = []
                if has_routes:
                    mixed.append("routing")
                if has_models:
                    mixed.append("database models")
                if has_classes:
                    mixed.append("multiple classes")

                observation = f"The file contains {fmeta.lines_count} lines"
                if mixed:
                    observation += f" and handles {', '.join(mixed)} simultaneously."
                else:
                    observation += "."

                concerns.append(
                    ArchitecturalConcern(
                        title=f"Large File ({fmeta.lines_count} lines)",
                        category="god_file",
                        file=rel_path,
                        observation=observation,
                        confidence=0.88,
                        suggested_action="Consider breaking down into smaller, focused modules (e.g. separating routes, business logic, and schemas).",
                    )
                )

        # 3. Missing Tests Warning
        if inventory.total_files > 15 and len(inventory.test_files) == 0:
            concerns.append(
                ArchitecturalConcern(
                    title="No Automated Test Suite Detected",
                    category="missing_tests",
                    file=None,
                    observation=f"Repository contains {inventory.total_files} files but no test directories or files were detected.",
                    confidence=0.90,
                    suggested_action="Add automated unit and integration tests (e.g., pytest, jest, or vitest).",
                )
            )

        return concerns
