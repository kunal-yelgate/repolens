"""CI/CD and Monorepo detectors."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from repolens.detectors.base import BaseDetector
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely


class CICDInfo(BaseModel):
    platform: str  # GitHub Actions, GitLab CI, Docker, etc.
    config_files: List[str] = Field(default_factory=list)
    has_docker: bool = False
    has_docker_compose: bool = False
    has_kubernetes: bool = False
    has_terraform: bool = False


class MonorepoInfo(BaseModel):
    is_monorepo: bool = False
    tool: Optional[str] = None  # Turborepo, Nx, pnpm workspaces, Yarn workspaces, Cargo workspace
    packages: List[str] = Field(default_factory=list)


class CICDDetector(BaseDetector):
    """Detects CI/CD pipelines, Docker, Kubernetes, and IaC tools."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> CICDInfo:
        platforms = []
        cfg_files = []
        has_docker = False
        has_compose = False
        has_k8s = False
        has_tf = False

        for rel_path in inventory.files:
            p_lower = rel_path.lower()
            if ".github/workflows" in p_lower:
                if "GitHub Actions" not in platforms:
                    platforms.append("GitHub Actions")
                cfg_files.append(rel_path)
            elif ".gitlab-ci.yml" in p_lower:
                platforms.append("GitLab CI")
                cfg_files.append(rel_path)
            elif "dockerfile" in p_lower:
                has_docker = True
                cfg_files.append(rel_path)
            elif "docker-compose" in p_lower or "compose.yml" in p_lower or "compose.yaml" in p_lower:
                has_compose = True
                cfg_files.append(rel_path)
            elif p_lower.endswith((".tf", ".tfvars")):
                has_tf = True
                cfg_files.append(rel_path)
            elif "k8s/" in p_lower or "kubernetes/" in p_lower:
                has_k8s = True
                cfg_files.append(rel_path)

        platform_str = ", ".join(platforms) if platforms else "None detected"
        return CICDInfo(
            platform=platform_str,
            config_files=cfg_files,
            has_docker=has_docker,
            has_docker_compose=has_compose,
            has_kubernetes=has_k8s,
            has_terraform=has_tf,
        )


class MonorepoDetector(BaseDetector):
    """Detects monorepo configurations and workspace packages."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> MonorepoInfo:
        is_mono = False
        tool = None
        packages: List[str] = []

        if "turbo.json" in inventory.files:
            is_mono = True
            tool = "Turborepo"
        elif "nx.json" in inventory.files:
            is_mono = True
            tool = "Nx"
        elif "pnpm-workspace.yaml" in inventory.files:
            is_mono = True
            tool = "pnpm workspaces"
        elif "lerna.json" in inventory.files:
            is_mono = True
            tool = "Lerna"

        # Check package.json workspaces
        if "package.json" in inventory.files:
            content = read_file_safely(inventory.files["package.json"].full_path)
            if content:
                try:
                    data = json.loads(content)
                    if "workspaces" in data:
                        is_mono = True
                        tool = tool or "npm/yarn workspaces"
                except Exception:
                    pass

        # Check Cargo workspace
        if "Cargo.toml" in inventory.files:
            content = read_file_safely(inventory.files["Cargo.toml"].full_path)
            if content and "[workspace]" in content:
                is_mono = True
                tool = "Cargo workspace"

        # Discover package subdirectories
        for d in inventory.directories:
            if d.startswith("packages/") or d.startswith("apps/") or d.startswith("services/"):
                if d.count("/") == 1:
                    packages.append(d)

        if packages and len(packages) >= 2:
            is_mono = True

        return MonorepoInfo(
            is_monorepo=is_mono,
            tool=tool,
            packages=packages,
        )
