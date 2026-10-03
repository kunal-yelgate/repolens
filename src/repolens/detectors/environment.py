"""Environment variable and configuration detector with strict secret redaction."""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set

from repolens.detectors.base import BaseDetector, EnvVarInfo
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely


class EnvironmentDetector(BaseDetector):
    """Detects required and optional environment variables and their referencing files."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> List[EnvVarInfo]:
        var_to_files: Dict[str, Set[str]] = defaultdict(set)
        example_vars: Set[str] = set()

        # 1. Parse sample / example env files
        for rel_path, fmeta in inventory.files.items():
            fname_lower = fmeta.filename.lower()
            if fname_lower in {".env.example", ".env.sample", ".env.template", ".env.local.example"}:
                content = read_file_safely(fmeta.full_path)
                if content:
                    for line in content.splitlines():
                        cleaned = line.strip()
                        if cleaned and not cleaned.startswith("#") and "=" in cleaned:
                            var_name = cleaned.split("=", 1)[0].strip()
                            if var_name:
                                example_vars.add(var_name)
                                var_to_files[var_name].add(rel_path)

        # 2. Add vars extracted from parsed source ASTs
        for rel_path, parsed in parsed_sources.items():
            for v in parsed.env_vars:
                if len(v) >= 2 and v.isupper() or "_" in v:
                    var_to_files[v].add(rel_path)

        # 3. Build EnvVarInfo list
        env_infos: List[EnvVarInfo] = []
        for vname, files in sorted(var_to_files.items()):
            # Required if present in .env.example or referenced in critical backend config files
            is_req = vname in example_vars or any("config" in f.lower() or "database" in f.lower() or "auth" in f.lower() for f in files)
            env_infos.append(
                EnvVarInfo(
                    name=vname,
                    required=is_req,
                    used_in_files=sorted(list(files)),
                )
            )

        return env_infos
