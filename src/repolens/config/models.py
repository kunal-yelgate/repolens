"""Configuration models for RepoLens."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    name: Optional[str] = None
    root: Path = Field(default_factory=Path.cwd)
    description: Optional[str] = None


class AnalysisConfig(BaseModel):
    max_file_size: int = 500_000  # 500 KB
    max_depth: int = 15
    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=list)
    token_budget: int = 8000
    incremental: bool = False
    enable_ast: bool = True
    enable_security: bool = True


class AIConfig(BaseModel):
    provider: str = "none"  # none, ollama, openai, anthropic, gemini, groq
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 4096
    timeout: float = 60.0
    confirmed_cloud_usage: bool = False


class SecurityConfig(BaseModel):
    scan_secrets: bool = True
    scan_vulnerabilities: bool = True
    redact_secrets: bool = True
    entropy_check: bool = True


class OutputConfig(BaseModel):
    directory: Path = Field(default=Path("."))
    format: str = "markdown"  # markdown, json, terminal
    generate_diagrams: bool = True
    generate_api_doc: bool = True
    generate_testing_doc: bool = True
    generate_setup_doc: bool = True
    generate_architecture_doc: bool = True
    generate_onboarding_doc: bool = True


class RepoLensConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    cache_dir: Path = Field(default=Path(".repolens"))

    model_config = {
        "extra": "ignore"
    }
