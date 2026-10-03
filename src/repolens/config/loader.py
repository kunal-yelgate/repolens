"""Configuration loader for RepoLens."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from repolens.config.models import (
    AIConfig,
    AnalysisConfig,
    OutputConfig,
    ProjectConfig,
    RepoLensConfig,
    SecurityConfig,
)


def _unwrap_val(val: Any) -> Any:
    if val is not None and type(val).__name__ == "OptionInfo":
        return getattr(val, "default", None)
    return val


def load_config(
    root_dir: Optional[Path] = None,
    config_file: Optional[Path] = None,
    cli_overrides: Optional[Dict[str, Any]] = None,
) -> RepoLensConfig:
    """
    Load RepoLens configuration from file, environment variables, and CLI overrides.
    Priority: CLI Overrides > Environment Variables > Config File > Defaults
    """
    root_dir = _unwrap_val(root_dir)
    root = (root_dir or Path.cwd()).resolve()
    config_data: Dict[str, Any] = {}

    # Check for config files
    possible_files = [
        config_file,
        root / "repolens.toml",
        root / ".repolens.toml",
        root / ".repolens" / "config.toml",
    ]

    for cf in possible_files:
        if cf and Path(cf).exists() and Path(cf).is_file():
            try:
                with open(cf, "rb") as f:
                    config_data = tomllib.load(f)
                break
            except Exception:
                pass

    # Check pyproject.toml [tool.repolens]
    pyproject_file = root / "pyproject.toml"
    if not config_data and pyproject_file.exists():
        try:
            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)
                if "tool" in data and "repolens" in data["tool"]:
                    config_data = data["tool"]["repolens"]
        except Exception:
            pass

    # Build config sections
    project_dict = config_data.get("project", {})
    analysis_dict = config_data.get("analysis", {})
    ai_dict = config_data.get("ai", {})
    security_dict = config_data.get("security", {})
    output_dict = config_data.get("output", {})

    # Ensure project root is set
    project_dict.setdefault("root", root)
    if not project_dict.get("name"):
        project_dict["name"] = root.name

    # Apply environment variables
    env_provider = os.getenv("REPOLENS_LLM_PROVIDER") or os.getenv("REPOLENS_PROVIDER")
    if env_provider:
        ai_dict["provider"] = env_provider

    env_api_key = os.getenv("REPOLENS_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY")
    if env_api_key:
        ai_dict["api_key"] = env_api_key

    env_model = os.getenv("REPOLENS_MODEL")
    if env_model:
        ai_dict["model"] = env_model

    env_base_url = os.getenv("REPOLENS_BASE_URL") or os.getenv("OPENAI_BASE_URL")
    if env_base_url:
        ai_dict["base_url"] = env_base_url

    # Apply CLI overrides if present
    if cli_overrides:
        clean_overrides = {k: _unwrap_val(v) for k, v in cli_overrides.items()}
        out_dir = clean_overrides.get("output_dir")
        if out_dir is not None:
            output_dict["directory"] = Path(out_dir)
        fmt = clean_overrides.get("format")
        if fmt is not None:
            output_dict["format"] = fmt
        if clean_overrides.get("no_ai"):
            ai_dict["provider"] = "none"
        elif clean_overrides.get("provider"):
            ai_dict["provider"] = clean_overrides["provider"]
        if clean_overrides.get("model"):
            ai_dict["model"] = clean_overrides["model"]
        if clean_overrides.get("incremental") is not None:
            analysis_dict["incremental"] = clean_overrides["incremental"]
        if clean_overrides.get("depth") is not None:
            analysis_dict["max_depth"] = clean_overrides["depth"]

    project = ProjectConfig(**project_dict)
    analysis = AnalysisConfig(**analysis_dict)
    ai = AIConfig(**ai_dict)
    security = SecurityConfig(**security_dict)
    output = OutputConfig(**output_dict)

    return RepoLensConfig(
        project=project,
        analysis=analysis,
        ai=ai,
        security=security,
        output=output,
        cache_dir=root / ".repolens",
    )
