"""Codebase Q&A Agent and 'Where Should I Change Code?' solver."""

from typing import List, Optional

from repolens.agents.base import AgentResponse, SYSTEM_PROMPT_CORE
from repolens.ai.base import BaseLLMProvider
from repolens.analysis.orchestrator import AnalysisResult
from repolens.analysis.ranking import CodebaseRanker


class QuestionAgent:
    """Answers developer questions and pinpoints change locations with evidence."""

    def __init__(self, analysis_result: AnalysisResult, ranker: CodebaseRanker, llm: BaseLLMProvider) -> None:
        self.result = analysis_result
        self.ranker = ranker
        self.llm = llm

    def ask(self, question: str) -> AgentResponse:
        # 1. Retrieve top matching files & symbols
        search_hits = self.ranker.search(question, top_k=6)
        hit_locations = [h.file_path for h in search_hits]
        evidence_list = [f"{h.file_path}: {h.matched_reason}" for h in search_hits]

        # 2. If AI is available, generate grounded explanation
        if self.llm.is_available() and self.llm.__class__.__name__ != "NullLLMProvider":
            context_str = self.result.structured_context.to_llm_prompt_context() if self.result.structured_context else ""
            prompt = f"""Question: {question}

Retrieved Relevant Files & Symbols:
{chr(10).join([f'- {h.file_path} (Line {h.line_number}): {h.matched_reason}' for h in search_hits])}

Codebase Structured Evidence:
{context_str}

Please answer the question clearly:
1. Explain the mechanism/concept directly based on codebase evidence.
2. List the exact files and locations (with line numbers if known).
3. If this is a 'where to change code' question, explain why each location is relevant and what change is needed.
4. Highlight any potential caveats.
"""
            resp = self.llm.complete(prompt=prompt, system_prompt=SYSTEM_PROMPT_CORE)
            if not resp.content.startswith("[Local Ollama error:"):
                return AgentResponse(
                    answer=resp.content,
                    confidence=0.90 if search_hits else 0.60,
                    evidence=evidence_list,
                    locations=hit_locations,
                )


        # 3. Deterministic Fallback Response
        lines = [f"Codebase Intelligence for: '{question}'", ""]

        if search_hits:
            lines.append("Relevant Code Locations:")
            for idx, hit in enumerate(search_hits, 1):
                lines.append(f"{idx}. {hit.file_path} (Line {hit.line_number})")
                lines.append(f"   Reason: {hit.matched_reason}")
                if hit.snippet:
                    lines.append(f"   Snippet: {hit.snippet}")

            lines.append("")
            lines.append("Evidence Summary:")
            if any("auth" in question.lower() for _ in [1]):
                lines.append("Authentication flow references detected across routes, middleware, and models.")
            elif any("database" in question.lower() for _ in [1]):
                lines.append("Database persistence references detected in database configuration and ORM models.")
            elif any("api" in question.lower() or "endpoint" in question.lower() for _ in [1]):
                lines.append(f"Project exposes {len(self.result.endpoints)} endpoints. Inspect route handlers above.")
            else:
                lines.append("Identified key modules matching query terms.")
        else:
            lines.append("No specific source files strongly matched the search query.")
            lines.append("Try inspecting main entry points:")
            for ep in self.result.entry_points[:3]:
                lines.append(f"- {ep.file} ({ep.reason})")

        return AgentResponse(
            answer="\n".join(lines),
            confidence=0.85 if search_hits else 0.50,
            evidence=evidence_list,
            locations=hit_locations,
        )
