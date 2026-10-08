"""Cache management for incremental analysis and performance."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import ensure_dir, safe_write_text


class CacheManager:
    """Manages cached file hashes, parsed AST metadata, and past analysis reports in `.repolens/`."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir.resolve()
        self.index_file = self.cache_dir / "index.json"
        self.cache_data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.cache_data = json.load(f)
            except Exception:
                self.cache_data = {}

    def save(self, parsed_sources: Dict[str, ParsedSource], inventory: RepositoryInventory) -> None:
        """Save current parsed sources and file hashes."""
        ensure_dir(self.cache_dir)
        data = {
            "version": "1.0",
            "files": {
                rel_path: {
                    "hash": inventory.files[rel_path].content_hash,
                    "parsed": parsed.model_dump(),
                }
                for rel_path, parsed in parsed_sources.items()
            },
        }
        safe_write_text(self.index_file, json.dumps(data, indent=2))

    def get_cached_parsed_source(self, rel_path: str, current_hash: str) -> Optional[ParsedSource]:
        """Return cached ParsedSource if file hash matches."""
        files_cache = self.cache_data.get("files", {})
        item = files_cache.get(rel_path)
        if item and item.get("hash") == current_hash and item.get("parsed"):
            try:
                return ParsedSource(**item["parsed"])
            except Exception:
                return None
        return None
