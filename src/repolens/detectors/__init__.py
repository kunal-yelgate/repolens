"""Detectors module for RepoLens."""

from repolens.detectors.api import APIDetector, DiscoveredEndpoint
from repolens.detectors.base import (
    ArchitecturalConcern,
    ArchitectureFinding,
    BaseDetector,
    DatabaseInfo,
    EntryPointInfo,
    EnvVarInfo,
    FindingEvidence,
    ProjectCommandsInfo,
    TestFrameworkInfo,
)
from repolens.detectors.cicd import CICDDetector, CICDInfo, MonorepoDetector, MonorepoInfo
from repolens.detectors.commands import CommandDetector
from repolens.detectors.database import DatabaseDetector
from repolens.detectors.entrypoint import EntryPointDetector
from repolens.detectors.environment import EnvironmentDetector
from repolens.detectors.framework import FrameworkDetector
from repolens.detectors.language import LanguageDetector
from repolens.detectors.problems import ArchitecturalProblemsDetector
from repolens.detectors.project_type import ProjectTypeDetector

__all__ = [
    "BaseDetector",
    "FindingEvidence",
    "EntryPointInfo",
    "DatabaseInfo",
    "ArchitectureFinding",
    "EnvVarInfo",
    "TestFrameworkInfo",
    "ProjectCommandsInfo",
    "ArchitecturalConcern",
    "DiscoveredEndpoint",
    "CICDInfo",
    "MonorepoInfo",
    "LanguageDetector",
    "FrameworkDetector",
    "ProjectTypeDetector",
    "EntryPointDetector",
    "DatabaseDetector",
    "APIDetector",
    "TestingDetector",
    "EnvironmentDetector",
    "CommandDetector",
    "CICDDetector",
    "MonorepoDetector",
    "ArchitecturalProblemsDetector",
]
