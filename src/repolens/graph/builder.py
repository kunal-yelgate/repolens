"""Repository Knowledge Graph Builder using NetworkX."""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import networkx as nx

from repolens.graph.models import (
    EntityType,
    GraphEdge,
    GraphNode,
    RelationType,
)
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory


class KnowledgeGraph:
    """Directed Knowledge Graph representing the codebase structure and relationships."""

    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()
        self.nodes_by_id: Dict[str, GraphNode] = {}
        self.edges_list: List[GraphEdge] = []

    def add_node(self, node: GraphNode) -> None:
        self.nodes_by_id[node.id] = node
        self.graph.add_node(
            node.id,
            label=node.label,
            entity_type=node.entity_type.value,
            **node.properties,
        )

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges_list.append(edge)
        self.graph.add_edge(
            edge.source,
            edge.target,
            relation=edge.relation.value,
            **edge.properties,
        )

    def get_neighbors(self, node_id: str) -> List[str]:
        if node_id in self.graph:
            return list(self.graph.successors(node_id))
        return []

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find simple cycles among File/Module nodes in the graph."""
        file_subgraph = nx.DiGraph()
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") == RelationType.IMPORTS.value:
                file_subgraph.add_edge(u, v)

        try:
            cycles = list(nx.simple_cycles(file_subgraph))
            return [c for c in cycles if len(c) > 1][:20]
        except Exception:
            return []


class KnowledgeGraphBuilder:
    """Builds a KnowledgeGraph from RepositoryInventory and parsed sources."""

    def build(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> KnowledgeGraph:
        kg = KnowledgeGraph()

        # 1. Add Repository Node
        repo_node_id = f"repo:{inventory.name}"
        kg.add_node(
            GraphNode(
                id=repo_node_id,
                label=inventory.name,
                entity_type=EntityType.REPOSITORY,
                properties={"total_files": inventory.total_files, "total_lines": inventory.total_lines},
            )
        )

        # 2. Add Directory Nodes & CONTAINS edges
        for dir_path in inventory.directories:
            dir_node_id = f"dir:{dir_path}"
            kg.add_node(
                GraphNode(
                    id=dir_node_id,
                    label=dir_path,
                    entity_type=EntityType.DIRECTORY,
                )
            )
            # Link root or parent dir
            if dir_path == ".":
                kg.add_edge(
                    GraphEdge(
                        source=repo_node_id,
                        target=dir_node_id,
                        relation=RelationType.CONTAINS,
                    )
                )
            else:
                parent = str(Path(dir_path).parent.as_posix())
                parent_id = f"dir:{parent}" if parent != "." else "dir:."
                if parent_id in kg.nodes_by_id:
                    kg.add_edge(
                        GraphEdge(
                            source=parent_id,
                            target=dir_node_id,
                            relation=RelationType.CONTAINS,
                        )
                    )

        # 3. Add File Nodes
        all_rel_paths = set(inventory.files.keys())

        for rel_path, fmeta in inventory.files.items():
            file_node_id = f"file:{rel_path}"
            kg.add_node(
                GraphNode(
                    id=file_node_id,
                    label=fmeta.filename,
                    entity_type=EntityType.FILE,
                    properties={
                        "path": rel_path,
                        "lines": fmeta.lines_count,
                        "is_entrypoint": fmeta.is_entrypoint_candidate,
                        "is_test": fmeta.is_test,
                    },
                )
            )
            parent_dir = str(Path(rel_path).parent.as_posix())
            parent_id = f"dir:{parent_dir}" if parent_dir != "." else "dir:."
            if parent_id in kg.nodes_by_id:
                kg.add_edge(
                    GraphEdge(
                        source=parent_id,
                        target=file_node_id,
                        relation=RelationType.CONTAINS,
                    )
                )

        # 4. Add Symbols (Classes, Functions, Routes, Env Vars) & IMPORTS Edges
        for rel_path, parsed in parsed_sources.items():
            file_node_id = f"file:{rel_path}"

            # Routes
            for route in parsed.routes:
                route_id = f"api:{route.http_method} {route.path}"
                kg.add_node(
                    GraphNode(
                        id=route_id,
                        label=f"{route.http_method} {route.path}",
                        entity_type=EntityType.API,
                        properties={"framework": route.framework, "auth": route.auth_required},
                    )
                )
                kg.add_edge(
                    GraphEdge(
                        source=file_node_id,
                        target=route_id,
                        relation=RelationType.EXPOSES,
                    )
                )

            # Env vars
            for ev in parsed.env_vars:
                ev_id = f"env:{ev}"
                if ev_id not in kg.nodes_by_id:
                    kg.add_node(
                        GraphNode(
                            id=ev_id,
                            label=ev,
                            entity_type=EntityType.ENVIRONMENT_VARIABLE,
                        )
                    )
                kg.add_edge(
                    GraphEdge(
                        source=file_node_id,
                        target=ev_id,
                        relation=RelationType.USES,
                    )
                )

            # DB Models
            for dbm in parsed.db_models:
                dbm_id = f"model:{dbm}"
                if dbm_id not in kg.nodes_by_id:
                    kg.add_node(
                        GraphNode(
                            id=dbm_id,
                            label=dbm,
                            entity_type=EntityType.DATABASE,
                        )
                    )
                kg.add_edge(
                    GraphEdge(
                        source=file_node_id,
                        target=dbm_id,
                        relation=RelationType.USES,
                    )
                )

            # Resolve imports to other files in repository
            for imp in parsed.imports:
                target_file = self._resolve_import_to_file(rel_path, imp.module, all_rel_paths)
                if target_file:
                    target_id = f"file:{target_file}"
                    if target_id in kg.nodes_by_id and target_id != file_node_id:
                        kg.add_edge(
                            GraphEdge(
                                source=file_node_id,
                                target=target_id,
                                relation=RelationType.IMPORTS,
                            )
                        )

        return kg

    def _resolve_import_to_file(
        self,
        current_file: str,
        module_path: str,
        all_files: Set[str],
    ) -> Optional[str]:
        """Attempt to resolve a module import string to an existing file in the workspace."""
        clean_mod = module_path.replace(".", "/")
        current_dir = str(Path(current_file).parent.as_posix())

        # Relative import
        if module_path.startswith("."):
            levels = len(module_path) - len(module_path.lstrip("."))
            cur = Path(current_file).parent
            for _ in range(levels - 1):
                cur = cur.parent
            base_dir = cur.as_posix()
            mod_part = module_path.lstrip(".").replace(".", "/")
            candidate_base = f"{base_dir}/{mod_part}" if base_dir != "." else mod_part
        else:
            candidate_base = clean_mod

        candidate_base = candidate_base.lstrip("/")

        # Check standard file extensions
        for ext in [".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rs"]:
            candidate = f"{candidate_base}{ext}"
            if candidate in all_files:
                return candidate
            candidate_idx = f"{candidate_base}/index{ext}"
            if candidate_idx in all_files:
                return candidate_idx
            candidate_init = f"{candidate_base}/__init__{ext}"
            if candidate_init in all_files:
                return candidate_init

            # Also check relative to current dir
            rel_candidate = f"{current_dir}/{candidate_base}{ext}"
            if rel_candidate in all_files:
                return rel_candidate

            # Check under src/ or app/
            for prefix in ["src/", "app/", "lib/"]:
                prefixed = f"{prefix}{candidate_base}{ext}"
                if prefixed in all_files:
                    return prefixed

        return None
