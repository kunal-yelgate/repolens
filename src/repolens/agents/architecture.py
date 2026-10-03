"""Architecture and Onboarding reasoning agents."""

from typing import Dict, List, Optional

from repolens.agents.base import AgentResponse, SYSTEM_PROMPT_CORE
from repolens.ai.base import BaseLLMProvider
from repolens.analysis.orchestrator import AnalysisResult


class ArchitectureAgent:
    """Explains high-level architecture, module relationships, and data flows."""

    def __init__(self, analysis_result: AnalysisResult, llm: BaseLLMProvider) -> None:
        self.result = analysis_result
        self.llm = llm

    def explain(self, focus_area: Optional[str] = None) -> AgentResponse:
        repo = self.result.repository
        fw_str = ", ".join(repo.frameworks) if repo.frameworks else "None detected"
        ptype_str = ", ".join(repo.project_types)

        if self.llm.is_available() and self.llm.__class__.__name__ != "NullLLMProvider":
            context_str = self.result.structured_context.to_llm_prompt_context() if self.result.structured_context else ""
            prompt = f"""Explain the architecture of {repo.name} based on the evidence below.
Focus Area: {focus_area or 'Complete Architecture'}

Codebase Evidence:
{context_str}

Please generate a clear architectural breakdown covering:
1. High-Level Architecture
2. Key Components & Responsibilities
3. Request & Data Flow
4. Database & State Management
5. Potential Architectural Concerns
"""
            resp = self.llm.complete(prompt=prompt, system_prompt=SYSTEM_PROMPT_CORE)
            return AgentResponse(
                answer=resp.content,
                confidence=0.92,
                evidence=[f"Architecture: {a.architecture}" for a in self.result.architecture],
                locations=[ep.file for ep in self.result.entry_points],
            )

        # Deterministic generation
        lines = [
            f"Architecture Overview: {repo.name}",
            "=" * 50,
            f"Project Type: {ptype_str}",
            f"Frameworks: {fw_str}",
            "",
            "High-Level Components:",
        ]
        for finding in self.result.architecture:
            lines.append(f"• {finding.architecture} (Confidence: {int(finding.confidence * 100)}%)")
            for ev in finding.evidence:
                lines.append(f"  - {ev}")

        lines.extend(["", "Architecture Diagram:", self.result.ascii_architecture])

        if self.result.entry_points:
            lines.extend(["", "Main Entry Points:"])
            for ep in self.result.entry_points:
                lines.append(f"• {ep.file} ({ep.type}): {ep.reason}")

        if self.result.database:
            lines.extend(["", "Database & Persistence:"])
            for db in self.result.database:
                lines.append(f"• {db.technology} (ORM: {db.orm or 'None'}) - Models: {len(db.models)} detected")

        if self.result.architectural_concerns:
            lines.extend(["", "Potential Architectural Concerns:"])
            for c in self.result.architectural_concerns:
                lines.append(f"• [{c.category.upper()}] {c.title}: {c.observation}")

        return AgentResponse(
            answer="\n".join(lines),
            confidence=0.90,
            evidence=[f"Architecture: {a.architecture}" for a in self.result.architecture],
            locations=[ep.file for ep in self.result.entry_points],
        )


class OnboardingAgent:
    """Generates developer onboarding guide (ONBOARDING.md)."""

    def __init__(self, analysis_result: AnalysisResult, llm: BaseLLMProvider) -> None:
        self.result = analysis_result
        self.llm = llm

    def generate_guide(self) -> str:
        repo = self.result.repository
        commands = self.result.commands

        lines = [
            f"# Developer Onboarding Guide — {repo.name}",
            "",
            "## 1. What this project does",
            f"**{repo.name}** is a **{', '.join(repo.project_types)}** with {repo.total_files} files and {repo.total_lines} lines of code.",
            "",
            "## 2. Technology Stack",
        ]
        for lang, pct in repo.languages.items():
            lines.append(f"- **{lang}**: {pct}%")
        if repo.frameworks:
            lines.append(f"- **Frameworks & Libraries**: {', '.join(repo.frameworks)}")

        lines.extend([
            "",
            "## 3. Repository Structure",
            "```text",
            self.result.ascii_tree,
            "```",
            "",
            "## 4. How the Application Starts (Entry Points)",
        ])
        for ep in self.result.entry_points:
            lines.append(f"- `{ep.file}`: {ep.reason}")

        lines.extend([
            "",
            "## 5. Architecture & Data Flow",
            "```text",
            self.result.ascii_architecture,
            "```",
            "",
            "## 6. How to Run Locally",
        ])
        for label, cmd in commands.install.items():
            lines.append(f"**Install Dependencies ({label})**:\n```bash\n{cmd}\n```")
        for label, cmd in commands.dev.items():
            lines.append(f"**Development Server ({label})**:\n```bash\n{cmd}\n```")

        lines.extend([
            "",
            "## 7. How to Run Tests",
        ])
        for label, cmd in commands.test.items():
            lines.append(f"**Run Tests ({label})**:\n```bash\n{cmd}\n```")

        lines.extend([
            "",
            "## 8. Where to Make Changes",
            "- **To add or modify API routes**: Look in route handlers listed in `API.md`.",
            "- **To update database schemas**: Check models in database persistence layer.",
            "- **To configure environment**: Inspect `.env.example`.",
            "",
            "## 9. Things to Be Careful About",
        ])
        if self.result.architectural_concerns:
            for c in self.result.architectural_concerns:
                lines.append(f"- **{c.title}**: {c.observation} ({c.suggested_action})")
        else:
            lines.append("- Ensure environment variables are configured before running development server.")

        return "\n".join(lines)
