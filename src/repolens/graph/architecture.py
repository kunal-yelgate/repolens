"""Architecture graph representation, ASCII diagrams, and Mermaid generators."""

from typing import Dict, List, Optional


class ArchitectureDiagramGenerator:
    """Generates ASCII and Mermaid architecture diagrams based on detected codebase layers."""

    @staticmethod
    def generate_ascii(
        frontend: Optional[str] = None,
        api_layer: Optional[str] = None,
        service_layer: Optional[str] = None,
        database: Optional[str] = None,
        cache: Optional[str] = None,
        auth: Optional[str] = None,
    ) -> str:
        """Generate a clean ASCII box diagram."""
        lines: List[str] = []

        if frontend:
            lines.append("┌───────────────────────────────────┐")
            lines.append(f"│  Frontend: {frontend:<23}│")
            lines.append("└─────────────────┬─────────────────┘")
            lines.append("                  │ HTTP / WebSocket")
            lines.append("                  ↓")

        if api_layer or not frontend:
            api_title = api_layer or "API / Routing Layer"
            lines.append("┌───────────────────────────────────┐")
            lines.append(f"│  API Layer: {api_title:<22}│")
            lines.append("└─────────────────┬─────────────────┘")
            lines.append("                  │")
            lines.append("                  ↓")

        if auth:
            lines.append(f"  [ Auth & Security: {auth} ]")
            lines.append("                  │")
            lines.append("                  ↓")

        if service_layer:
            lines.append("┌───────────────────────────────────┐")
            lines.append(f"│  Services: {service_layer:<23}│")
            lines.append("└─────────────────┬─────────────────┘")
            lines.append("                  │")
            lines.append("                  ↓")

        db_title = database or "Data / Persistence Layer"
        lines.append("┌───────────────────────────────────┐")
        lines.append(f"│  Database: {db_title:<23}│")
        lines.append("└───────────────────────────────────┘")

        if cache:
            lines.append(f"  + Cache: {cache}")

        return "\n".join(lines)

    @staticmethod
    def generate_mermaid(
        frontend: Optional[str] = None,
        api_layer: Optional[str] = None,
        service_layer: Optional[str] = None,
        database: Optional[str] = None,
        cache: Optional[str] = None,
        auth: Optional[str] = None,
    ) -> str:
        """Generate Mermaid markdown diagram."""
        lines = ["```mermaid", "graph TD"]

        if frontend:
            lines.append('    Frontend["Frontend (' + frontend + ')"]')
            lines.append('    API["API Layer (' + (api_layer or "REST / GraphQL") + ')"]')
            lines.append("    Frontend -->|HTTP / JSON| API")
        else:
            lines.append('    API["API Layer (' + (api_layer or "REST API") + ')"]')

        if auth:
            lines.append('    Auth["Auth Middleware (' + auth + ')"]')
            lines.append("    API --> Auth")
            current_parent = "Auth"
        else:
            current_parent = "API"

        if service_layer:
            lines.append('    Services["Service Layer (' + service_layer + ')"]')
            lines.append(f"    {current_parent} --> Services")
            current_parent = "Services"

        if database:
            lines.append('    DB[("Database (' + database + ')")]')
            lines.append(f"    {current_parent} --> DB")

        if cache:
            lines.append('    Cache[("Cache (' + cache + ')")]')
            lines.append(f"    {current_parent} --> Cache")

        lines.append("```")
        return "\n".join(lines)
