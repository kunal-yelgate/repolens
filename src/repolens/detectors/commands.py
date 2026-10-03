"""Setup, development, testing, and build command detector."""

import json
from pathlib import Path
from typing import Dict, List

from repolens.detectors.base import BaseDetector, ProjectCommandsInfo
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely


class CommandDetector(BaseDetector):
    """Infers correct install, development, testing, and build commands."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> ProjectCommandsInfo:
        commands = ProjectCommandsInfo()

        has_frontend_dir = "frontend" in inventory.directories or "client" in inventory.directories
        has_backend_dir = "backend" in inventory.directories or "server" in inventory.directories or "app" in inventory.directories

        # 1. Python Commands
        has_reqs = "requirements.txt" in inventory.files or "backend/requirements.txt" in inventory.files
        has_pyproject = "pyproject.toml" in inventory.files or "backend/pyproject.toml" in inventory.files
        has_poetry = "poetry.lock" in inventory.files or "backend/poetry.lock" in inventory.files
        has_pipenv = "Pipfile" in inventory.files or "backend/Pipfile" in inventory.files

        if has_poetry:
            commands.install["Python"] = "poetry install"
            commands.dev["Python"] = "poetry run uvicorn app.main:app --reload"
            commands.test["Python"] = "poetry run pytest"
        elif has_pipenv:
            commands.install["Python"] = "pipenv install"
            commands.dev["Python"] = "pipenv run python main.py"
            commands.test["Python"] = "pipenv run pytest"
        elif has_pyproject:
            commands.install["Python"] = "pip install -e ."
            commands.dev["Python"] = "python -m repolens analyze"
            commands.test["Python"] = "pytest"
        elif has_reqs:
            req_file = "backend/requirements.txt" if "backend/requirements.txt" in inventory.files else "requirements.txt"
            label = "Backend" if has_backend_dir else "Python"
            commands.install[label] = f"pip install -r {req_file}"
            commands.dev[label] = "uvicorn app.main:app --reload"
            commands.test[label] = "pytest"

        # 2. Node / JS / TS Commands
        for rel_path, fmeta in inventory.files.items():
            if fmeta.filename.lower() == "package.json":
                content = read_file_safely(fmeta.full_path)
                parent_dir = str(Path(rel_path).parent.as_posix())
                label = "Root" if parent_dir == "." else parent_dir.capitalize()

                pkg_manager = "npm"
                if f"{parent_dir}/pnpm-lock.yaml" in inventory.files or "pnpm-lock.yaml" in inventory.files:
                    pkg_manager = "pnpm"
                elif f"{parent_dir}/yarn.lock" in inventory.files or "yarn.lock" in inventory.files:
                    pkg_manager = "yarn"
                elif f"{parent_dir}/bun.lockb" in inventory.files or "bun.lockb" in inventory.files:
                    pkg_manager = "bun"

                cd_prefix = f"cd {parent_dir} && " if parent_dir != "." else ""
                commands.install[label] = f"{cd_prefix}{pkg_manager} install"

                if content:
                    try:
                        data = json.loads(content)
                        scripts = data.get("scripts", {})
                        if "dev" in scripts:
                            commands.dev[label] = f"{cd_prefix}{pkg_manager} run dev"
                        elif "start" in scripts:
                            commands.dev[label] = f"{cd_prefix}{pkg_manager} start"

                        if "test" in scripts:
                            commands.test[label] = f"{cd_prefix}{pkg_manager} test"

                        if "build" in scripts:
                            commands.build[label] = f"{cd_prefix}{pkg_manager} run build"
                    except Exception:
                        pass

        # 3. Go Commands
        if "go.mod" in inventory.files:
            commands.install["Go"] = "go mod download"
            commands.dev["Go"] = "go run ."
            commands.test["Go"] = "go test ./..."
            commands.build["Go"] = "go build ."

        # 4. Rust Commands
        if "Cargo.toml" in inventory.files:
            commands.install["Rust"] = "cargo build"
            commands.dev["Rust"] = "cargo run"
            commands.test["Rust"] = "cargo test"
            commands.build["Rust"] = "cargo build --release"

        return commands
