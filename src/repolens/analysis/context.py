"""Context aggregation for LLM reasoning and staged token budgeting."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from repolens.detectors.base import (
    ArchitecturalConcern,
    DatabaseInfo,
    EntryPointInfo,
    EnvVarInfo,
    ProjectCommandsInfo,
    TestFrameworkInfo,
)
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely


class StructuredCodebaseContext(BaseModel):
    project_name: str
    total_files: int
    total_lines: int
    languages: Dict[str, float]
    frameworks: List[str]
    project_types: List[str]
    entry_points: List[EntryPointInfo]
    database: List[DatabaseInfo]
    endpoints_sample: List[str]
    env_vars: List[str]
    test_frameworks: List[str]
    commands: ProjectCommandsInfo
    architecture_findings: List[str]
    concerns: List[str]
    important_file_snippets: Dict[str, str] = Field(default_factory=dict)

    def to_llm_prompt_context(self) -> str:
        """Convert structured context to a concise, structured prompt section."""
        lines = [
            f"=== PROJECT: {self.project_name} ===",
            f"Type: {', '.join(self.project_types)}",
            f"Languages: {', '.join([f'{k} ({v}%)' for k, v in self.languages.items()])}",
            f"Frameworks: {', '.join(self.frameworks) if self.frameworks else 'None detected'}",
            "",
            "=== ENTRY POINTS ===",
        ]
        for ep in self.entry_points:
            lines.append(f"- {ep.file} ({ep.type}): {ep.reason}")

        lines.extend(["", "=== DATABASE & PERSISTENCE ==="])
        if self.database:
            for db in self.database:
                lines.append(f"- {db.technology} (ORM: {db.orm or 'None'}) - Models: {', '.join(db.models[:10])}")
        else:
            lines.append("- None detected")

        lines.extend(["", "=== API ENDPOINTS (Sample) ==="])
        if self.endpoints_sample:
            for ep in self.endpoints_sample[:15]:
                lines.append(f"- {ep}")
        else:
            lines.append("- None detected")

        lines.extend(["", "=== ENVIRONMENT VARIABLES ==="])
        lines.append(f"- {', '.join(self.env_vars[:20]) if self.env_vars else 'None detected'}")

        lines.extend(["", "=== COMMANDS ==="])
        lines.append(f"Install: {self.commands.install}")
        lines.append(f"Dev: {self.commands.dev}")
        lines.append(f"Test: {self.commands.test}")

        if self.important_file_snippets:
            lines.extend(["", "=== KEY SOURCE SNIPPETS ==="])
            for fpath, snippet in self.important_file_snippets.items():
                lines.append(f"--- {fpath} ---")
                lines.append(snippet[:800])
                lines.append("-----------------")

        return "\n".join(lines)
