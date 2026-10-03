"""Language detection with lines of code and percentage computation."""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from repolens.detectors.base import BaseDetector
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory

EXTENSION_LANGUAGE_MAP: Dict[str, str] = {
    ".py": "Python",
    ".pyw": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".mts": "TypeScript",
    ".cts": "TypeScript",
    ".tsx": "TypeScript",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".hpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SASS",
    ".less": "LESS",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".md": "Markdown",
    ".dockerfile": "Dockerfile",
    ".proto": "Protocol Buffers",
    ".dart": "Dart",
    ".lua": "Lua",
    ".r": "R",
    ".scala": "Scala",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".erl": "Erlang",
    ".hrl": "Erlang",
    ".hs": "Haskell",
    ".lhs": "Haskell",
    ".clj": "Clojure",
    ".cljs": "Clojure",
    ".cljc": "Clojure",
    ".zig": "Zig",
    ".nim": "Nim",
    ".v": "V",
    ".jl": "Julia",
    ".ml": "OCaml",
    ".mli": "OCaml",
    ".fs": "F#",
    ".fsi": "F#",
    ".fsx": "F#",
    ".tf": "Terraform",
    ".hcl": "HCL",
    ".graphql": "GraphQL",
    ".gql": "GraphQL",
    ".sol": "Solidity",
    ".move": "Move",
    ".asm": "Assembly",
    ".s": "Assembly",
    ".cob": "COBOL",
    ".cbl": "COBOL",
    ".f90": "Fortran",
    ".f": "Fortran",
    ".lisp": "Lisp",
    ".cl": "Lisp",
    ".el": "Lisp",
}

CODE_LANGUAGES = {
    "Python", "JavaScript", "TypeScript", "Vue", "Svelte", "Go", "Rust", "Java", "Kotlin",
    "C", "C++", "C#", "PHP", "Ruby", "Swift", "Shell", "PowerShell", "Dart", "Scala", "Lua", "R",
    "Elixir", "Erlang", "Haskell", "Clojure", "Zig", "Nim", "V", "Julia", "OCaml", "F#",
    "Solidity", "Move", "Assembly", "COBOL", "Fortran", "Lisp",
}


class LanguageDetector(BaseDetector):
    """Detects languages and calculates breakdown by lines of code."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> Dict[str, float]:
        lang_lines: Dict[str, int] = defaultdict(int)

        for rel_path, fmeta in inventory.files.items():
            if fmeta.is_binary:
                continue

            ext = fmeta.extension.lower()
            fname_lower = fmeta.filename.lower()

            lang = None
            if fname_lower == "dockerfile":
                lang = "Dockerfile"
            elif fname_lower == "makefile":
                lang = "Makefile"
            else:
                lang = EXTENSION_LANGUAGE_MAP.get(ext)

            if lang:
                # Give primary weight to actual code languages, but record all
                lang_lines[lang] += max(fmeta.lines_count, 1)

        # Filter to code languages first if present
        code_lines = {l: cnt for l, cnt in lang_lines.items() if l in CODE_LANGUAGES}
        target_dict = code_lines if code_lines else lang_lines

        total_lines = sum(target_dict.values())
        if total_lines == 0:
            return {"Unknown": 100.0}

        breakdown: Dict[str, float] = {}
        for lang, count in sorted(target_dict.items(), key=lambda x: x[1], reverse=True):
            pct = round((count / total_lines) * 100, 1)
            if pct > 0.5:
                breakdown[lang] = pct

        return breakdown
