"""High-level repository scanner and structure generator."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from repolens.config.models import AnalysisConfig, RepoLensConfig
from repolens.scanner.files import scan_directory_tree
from repolens.scanner.ignore import IgnoreFilter
from repolens.scanner.metadata import FileMetadata, RepositoryInventory
from repolens.utils.logging import log_debug, log_info


class RepositoryScanner:
    """Orchestrates repository scanning and inventory building."""

    def __init__(self, config: RepoLensConfig) -> None:
        self.config = config
        self.root = config.project.root.resolve()
        self.ignore_filter = IgnoreFilter(
            root=self.root,
            custom_includes=config.analysis.include_patterns,
            custom_excludes=config.analysis.exclude_patterns,
        )

    def scan(
        self, progress_callback: Optional[Callable[[str], None]] = None
    ) -> RepositoryInventory:
        """Scan repository and return inventory."""
        log_debug(f"Scanning repository at {self.root}")
        inventory = scan_directory_tree(
            root=self.root,
            ignore_filter=self.ignore_filter,
            max_file_size=self.config.analysis.max_file_size,
            max_depth=self.config.analysis.max_depth,
            progress_callback=progress_callback,
        )
        log_info(
            f"Scanned {inventory.total_files:,} files across {inventory.total_directories:,} "
            f"directories ({inventory.total_lines:,} analyzed lines; "
            f"{inventory.skipped_large_files:,} oversized files skipped)"
        )
        return inventory

    def generate_smart_tree(self, inventory: RepositoryInventory, max_items_per_dir: int = 8) -> str:
        """
        Generate a clean, readable ASCII tree representation of the repository.
        Focuses on important architectural files, manifests, configs, and entrypoints.
        """
        lines: List[str] = [f"{inventory.name}/"]

        # Group files by immediate parent directory
        dir_to_files: Dict[str, List[FileMetadata]] = {}
        for file_meta in inventory.files.values():
            parent_dir = str(Path(file_meta.path).parent.as_posix())
            if parent_dir == ".":
                parent_dir = ""
            dir_to_files.setdefault(parent_dir, []).append(file_meta)

        # Get all unique directory paths, sorted
        all_dirs = sorted(
            [d for d in inventory.directories.keys() if d != "."],
            key=lambda d: (len(d.split("/")), d)
        )
        dir_to_subdirs: Dict[str, List[str]] = {}
        for directory in all_dirs:
            parent, _, _ = directory.rpartition("/")
            dir_to_subdirs.setdefault(parent, []).append(directory)

        # Top level files
        root_files = dir_to_files.get("", [])
        root_files_sorted = sorted(
            root_files,
            key=lambda f: (not f.is_entrypoint_candidate, not f.is_config, not f.is_documentation, f.filename)
        )

        # Render top level directories
        top_dirs = [d for d in all_dirs if "/" not in d]

        for i, d in enumerate(top_dirs):
            is_last_dir = (i == len(top_dirs) - 1) and not root_files
            dir_prefix = "└── " if is_last_dir else "├── "
            child_prefix = "    " if is_last_dir else "│   "
            lines.append(f"{dir_prefix}{d}/")

            # Show subdirectories/files inside top dir
            sub_files = dir_to_files.get(d, [])
            sub_dirs = dir_to_subdirs.get(d, [])

            displayed_items = 0
            for sd in sub_dirs:
                if displayed_items >= max_items_per_dir:
                    lines.append(f"{child_prefix}├── ... ({len(sub_dirs) - displayed_items} more dirs)")
                    break
                sub_name = sd.split("/")[1]
                lines.append(f"{child_prefix}├── {sub_name}/")
                # Show key files in sub dir
                deep_files = dir_to_files.get(sd, [])
                for df in deep_files[:3]:
                    lines.append(f"{child_prefix}│   ├── {df.filename}")
                if len(deep_files) > 3:
                    lines.append(f"{child_prefix}│   └── ... ({len(deep_files) - 3} more files)")
                displayed_items += 1

            for f in sub_files[:max_items_per_dir]:
                lines.append(f"{child_prefix}├── {f.filename}")
            if len(sub_files) > max_items_per_dir:
                lines.append(f"{child_prefix}└── ... ({len(sub_files) - max_items_per_dir} more files)")

        # Render root files
        for i, f in enumerate(root_files_sorted[:max_items_per_dir * 2]):
            is_last = (i == len(root_files_sorted) - 1)
            prefix = "└── " if is_last else "├── "
            lines.append(f"{prefix}{f.filename}")

        if len(root_files_sorted) > max_items_per_dir * 2:
            lines.append(f"└── ... ({len(root_files_sorted) - max_items_per_dir * 2} more files)")

        return "\n".join(lines)
