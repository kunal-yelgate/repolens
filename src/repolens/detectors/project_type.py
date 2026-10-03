"""Project type classification (CLI, Full-stack, Backend API, Frontend, ML, etc.)."""

from typing import Dict, List, Set

from repolens.detectors.base import BaseDetector
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory


class ProjectTypeDetector(BaseDetector):
    """Classifies repository into primary and secondary project types."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> List[str]:
        types: Set[str] = set()

        has_frontend = False
        has_backend = False
        has_ml = False
        has_cli = False
        has_mobile = False
        has_desktop = False
        has_infra = False
        has_monorepo = False

        # Directory structure evidence
        dir_names = {d.lower() for d in inventory.directories.keys()}
        top_dirs = {d.split("/")[0].lower() for d in inventory.directories.keys() if d != "."}

        if bool({"frontend", "client", "ui", "web", "apps/web"} & top_dirs):
            has_frontend = True
        if bool({"backend", "server", "api", "services", "apps/api"} & top_dirs):
            has_backend = True
        if bool({"packages", "apps", "services"} & top_dirs) and len(top_dirs) > 2:
            has_monorepo = True
        if bool({"terraform", "k8s", "kubernetes", "ansible", "helm", "infra", "infrastructure"} & top_dirs):
            has_infra = True

        # File evidence
        for rel_path, fmeta in inventory.files.items():
            fname_lower = fmeta.filename.lower()
            path_lower = rel_path.lower()

            # CLI detection
            if fname_lower == "cli.py" or "cli/" in path_lower or "cmd/" in path_lower or "bin/" in path_lower:
                has_cli = True

            # Frontend evidence
            if fname_lower in {"next.config.js", "next.config.mjs", "vite.config.js", "vite.config.ts"} or "src/components" in path_lower or "src/pages" in path_lower or "src/app" in path_lower:
                has_frontend = True

            # ML evidence
            if fname_lower in {"model.pt", "weights.h5", "dataset.csv", "training.py", "train.py"} or "models/train" in path_lower:
                has_ml = True

            # Mobile evidence
            if "android/" in path_lower or "ios/" in path_lower or fname_lower in {"app.json", "eas.json"} or "react-native" in path_lower:
                has_mobile = True

            # Desktop evidence
            if fname_lower in {"tauri.conf.json", "electron-builder.yml"}:
                has_desktop = True

        # Parsed sources evidence
        total_routes = sum(len(p.routes) for p in parsed_sources.values())
        if total_routes > 0:
            has_backend = True

        # Synthesis
        if has_frontend and has_backend:
            types.add("Full-stack web application")
        elif has_backend:
            types.add("Backend API")
        elif has_frontend:
            types.add("Frontend application")

        if has_cli:
            types.add("CLI tool")
        if has_ml:
            types.add("Machine Learning / Data Science")
        if has_mobile:
            types.add("Mobile application")
        if has_desktop:
            types.add("Desktop application")
        if has_infra:
            types.add("Infrastructure / DevOps")
        if has_monorepo:
            types.add("Monorepo")

        if not types:
            # Check if it's a library or unknown
            if "setup.py" in inventory.files or "pyproject.toml" in inventory.files or "package.json" in inventory.files:
                types.add("Library / Package")
            else:
                types.add("Software Repository")

        return sorted(list(types))
