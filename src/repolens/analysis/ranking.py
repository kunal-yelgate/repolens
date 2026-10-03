"""Codebase search and relevance ranking."""

import re
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely


class SearchResult(BaseModel):
    file_path: str
    relevance_score: float
    matched_reason: str
    line_number: int = 1
    snippet: Optional[str] = None


STOP_WORDS = {
    "where", "is", "the", "how", "what", "to", "in", "for", "a", "an", "and",
    "or", "of", "on", "with", "at", "by", "from", "up", "about", "into", "over",
    "after", "can", "should", "i", "my", "we", "our", "do", "does", "did", "this",
}


class CodebaseRanker:
    """Ranks codebase files and symbols against query terms using fuzzy token matching and graph importance."""

    def __init__(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> None:
        self.inventory = inventory
        self.parsed_sources = parsed_sources

    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        raw_terms = [t.lower() for t in re.split(r'[\s_\-/,.]+', query) if len(t) >= 2]
        content_terms = [t for t in raw_terms if t not in STOP_WORDS]
        query_terms = content_terms if content_terms else raw_terms
        if not query_terms:
            return []


        results: List[SearchResult] = []

        for rel_path, fmeta in self.inventory.files.items():
            if fmeta.is_binary:
                continue

            score = 0.0
            reasons = []
            best_line = 1
            best_snippet = None

            path_lower = rel_path.lower()
            filename_lower = fmeta.filename.lower()

            # 1. Path & Filename matches (highest weight)
            for term in query_terms:
                if term in filename_lower:
                    score += 50.0
                    reasons.append(f"Filename contains '{term}'")
                elif term in path_lower:
                    score += 25.0
                    reasons.append(f"Directory path contains '{term}'")

            # 2. Parsed symbols (Classes, Functions, Routes)
            parsed = self.parsed_sources.get(rel_path)
            if parsed:
                # Routes
                for route in parsed.routes:
                    for term in query_terms:
                        if term in route.path.lower() or term in route.handler_name.lower():
                            score += 40.0
                            reasons.append(f"Exposes endpoint: {route.http_method} {route.path}")
                            best_line = route.line_number

                # Classes
                for cls in parsed.classes:
                    for term in query_terms:
                        if term in cls.name.lower():
                            score += 35.0
                            reasons.append(f"Defines class '{cls.name}'")
                            best_line = cls.line_number

                # Functions
                for fn in parsed.functions:
                    for term in query_terms:
                        if term in fn.name.lower():
                            score += 30.0
                            reasons.append(f"Defines function '{fn.name}'")
                            best_line = fn.line_number

            # 3. Text content scanning
            content = read_file_safely(fmeta.full_path)
            if content:
                lines = content.splitlines()
                for idx, line in enumerate(lines[:500]):
                    line_lower = line.lower()
                    for term in query_terms:
                        if term in line_lower:
                            score += 2.0
                            if not best_snippet:
                                best_line = idx + 1
                                best_snippet = line.strip()

            if score > 0:
                results.append(
                    SearchResult(
                        file_path=rel_path,
                        relevance_score=score,
                        matched_reason="; ".join(reasons[:2]) if reasons else "Content match",
                        line_number=best_line,
                        snippet=best_snippet,
                    )
                )

        return sorted(results, key=lambda x: x.relevance_score, reverse=True)[:top_k]
