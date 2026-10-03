"""API endpoint detector and route aggregator."""

from typing import Dict, List
from pydantic import BaseModel, Field

from repolens.detectors.base import BaseDetector
from repolens.parsers.base import ParsedRoute, ParsedSource
from repolens.scanner.metadata import RepositoryInventory


class DiscoveredEndpoint(BaseModel):
    file_path: str
    line_number: int
    http_method: str
    path: str
    handler_name: str
    framework: str
    auth_required: bool = False


class APIDetector(BaseDetector):
    """Detects REST and web API routes across backend frameworks."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> List[DiscoveredEndpoint]:
        endpoints: List[DiscoveredEndpoint] = []

        for rel_path, parsed in parsed_sources.items():
            for route in parsed.routes:
                endpoints.append(
                    DiscoveredEndpoint(
                        file_path=rel_path,
                        line_number=route.line_number,
                        http_method=route.http_method,
                        path=route.path,
                        handler_name=route.handler_name,
                        framework=route.framework,
                        auth_required=route.auth_required,
                    )
                )

        # Sort by path then method
        return sorted(endpoints, key=lambda x: (x.path, x.http_method))
