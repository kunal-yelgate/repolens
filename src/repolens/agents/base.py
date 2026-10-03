"""AI reasoning agents for codebase understanding, Q&A, and onboarding."""

from typing import Dict, List, Optional
from pydantic import BaseModel

from repolens.ai.base import BaseLLMProvider
from repolens.analysis.orchestrator import AnalysisResult
from repolens.analysis.ranking import CodebaseRanker


class AgentResponse(BaseModel):
    answer: str
    confidence: float
    evidence: List[str]
    locations: List[str]


SYSTEM_PROMPT_CORE = """You are RepoLens, an autonomous software repository architecture and intelligence agent.
You are given structured facts, AST symbols, entry points, dependencies, and file evidence collected deterministically from a codebase.

CRITICAL RULES:
1. Ground every statement strictly in the provided codebase facts and source snippets.
2. NEVER hallucinate or invent files, APIs, packages, database models, or commands that are not in the context.
3. If information is missing or not detected with confidence, explicitly state "Unknown / Not detected in codebase".
4. Explicitly separate FACT (observed code) from INFERENCE (architectural interpretation).
5. Provide specific file paths and line numbers whenever possible.
"""
