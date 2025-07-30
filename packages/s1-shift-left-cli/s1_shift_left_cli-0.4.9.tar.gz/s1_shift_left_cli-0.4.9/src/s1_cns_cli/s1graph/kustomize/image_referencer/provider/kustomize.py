from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

from s1_cns_cli.s1graph.kubernetes.image_referencer.provider.k8s import SUPPORTED_K8S_IMAGE_RESOURCE_TYPES
from s1_cns_cli.s1graph.kustomize.image_referencer.base_provider import BaseKustomizeProvider

if TYPE_CHECKING:
    from networkx import DiGraph


class KustomizeProvider(BaseKustomizeProvider):
    def __init__(self, graph_connector: DiGraph, report_mutator_data: Dict[str, Dict[str, Any]]):
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=SUPPORTED_K8S_IMAGE_RESOURCE_TYPES,
            report_mutator_data=report_mutator_data
        )
