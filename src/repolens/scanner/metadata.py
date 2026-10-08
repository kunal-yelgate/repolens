"""File and directory metadata structures."""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    path: str  # Relative path with forward slashes
    full_path: Path
    filename: str
    extension: str
    size_bytes: int
    lines_count: int
    content_hash: str
    is_binary: bool = False
    language_guess: Optional[str] = None
    is_test: bool = False
    is_config: bool = False
    is_documentation: bool = False
    is_entrypoint_candidate: bool = False


class DirectoryMetadata(BaseModel):
    path: str  # Relative path with forward slashes
    full_path: Path
    file_count: int = 0
    dir_count: int = 0
    total_size_bytes: int = 0


class RepositoryInventory(BaseModel):
    root: Path
    name: str
    total_files: int = 0
    total_directories: int = 0
    total_lines: int = 0
    total_size_bytes: int = 0
    skipped_large_files: int = 0
    files: Dict[str, FileMetadata] = Field(default_factory=dict)
    directories: Dict[str, DirectoryMetadata] = Field(default_factory=dict)
    manifest_files: List[str] = Field(default_factory=list)
    config_files: List[str] = Field(default_factory=list)
    doc_files: List[str] = Field(default_factory=list)
    test_files: List[str] = Field(default_factory=list)
    has_git: bool = False
    git_branch: Optional[str] = None
