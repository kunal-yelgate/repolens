"""Dependency graph query engine and circular dependency analyzer."""

from typing import Dict, List, Optional, Set
import networkx as nx

from repolens.graph.builder import KnowledgeGraph
from repolens.graph.models import RelationType


class DependencyGraphAnalyzer:
    """Provides targeted dependency graph queries for CLI and reports."""

    def __init__(self, knowledge_graph: KnowledgeGraph) -> None:
        self.kg = knowledge_graph
        self.g = knowledge_graph.graph

    def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """Get outgoing imports and incoming dependents for a file."""
        node_id = f"file:{file_path}"
        imports: List[str] = []
        imported_by: List[str] = []

        if node_id in self.g:
            # Outgoing IMPORTS
            for succ in self.g.successors(node_id):
                edge_data = self.g.get_edge_data(node_id, succ)
                if edge_data and edge_data.get("relation") == RelationType.IMPORTS.value:
                    imports.append(succ.replace("file:", ""))

            # Incoming IMPORTS
            for pred in self.g.predecessors(node_id):
                edge_data = self.g.get_edge_data(pred, node_id)
                if edge_data and edge_data.get("relation") == RelationType.IMPORTS.value:
                    imported_by.append(pred.replace("file:", ""))

        return {
            "file": file_path,
            "imports": sorted(imports),
            "imported_by": sorted(imported_by),
        }

    def get_module_graph(self, module_prefix: str) -> Dict[str, List[str]]:
        """Get high-level module dependency mapping."""
        module_deps: Dict[str, Set[str]] = {}

        for u, v, data in self.g.edges(data=True):
            if data.get("relation") == RelationType.IMPORTS.value:
                u_clean = u.replace("file:", "")
                v_clean = v.replace("file:", "")

                if module_prefix and not u_clean.startswith(module_prefix):
                    continue

                u_mod = u_clean.split("/")[0] if "/" in u_clean else u_clean
                v_mod = v_clean.split("/")[0] if "/" in v_clean else v_clean

                if u_mod != v_mod:
                    module_deps.setdefault(u_mod, set()).add(v_mod)

        return {k: sorted(list(v)) for k, v in sorted(module_deps.items())}

    def format_ascii_graph(self, file_path: Optional[str] = None, module: Optional[str] = None) -> str:
        """Format an ASCII dependency representation."""
        if file_path:
            res = self.get_file_dependencies(file_path)
            lines = [f"File Dependency Graph: {file_path}", ""]
            lines.append("Imports:")
            if res["imports"]:
                for imp in res["imports"]:
                    lines.append(f"  └──> {imp}")
            else:
                lines.append("  (none detected)")

            lines.append("")
            lines.append("Imported By:")
            if res["imported_by"]:
                for imp_by in res["imported_by"]:
                    lines.append(f"  <─── {imp_by}")
            else:
                lines.append("  (none detected)")
            return "\n".join(lines)

        # High level module graph
        mod_deps = self.get_module_graph(module or "")
        lines = ["High-Level Module Dependency Graph:", ""]
        if not mod_deps:
            lines.append("  (no inter-module dependencies detected)")
        else:
            for mod, targets in mod_deps.items():
                lines.append(f"📦 {mod}")
                for t in targets:
                    lines.append(f"   └──> {t}")
        return "\n".join(lines)
