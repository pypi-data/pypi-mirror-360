from __future__ import annotations

import itertools
import os
from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Any, Mapping, Union, Generator

from s1_cns_cli.s1graph.common.graph.graph_builder import CustomAttributes
from s1_cns_cli.s1graph.common.images.image_referencer import Image

if TYPE_CHECKING:
    import networkx
    from typing_extensions import TypeAlias

_ExtractImagesCallableAlias: TypeAlias = Callable[["dict[str, Any]"], "list[str]"]


class GraphImageReferencerProvider:
    __slots__ = ("graph_connector", "supported_resource_types", "graph_framework")

    def __init__(self, graph_connector: Union[networkx.DiGraph],
                 supported_resource_types: dict[str, _ExtractImagesCallableAlias] | Mapping[
                     str, _ExtractImagesCallableAlias]):
        self.graph_connector = graph_connector
        self.supported_resource_types = supported_resource_types
        self.graph_framework = os.environ.get('SENTINELONE_CNS_GRAPH_FRAMEWORK', 'NETWORKX')

    @abstractmethod
    def extract_images_from_resources(self) -> list[Image]:
        pass

    def extract_nodes(self) -> networkx.Graph | None:
        # the default value of the graph framework is 'NETWORKX'
        if self.graph_framework == 'NETWORKX':
            return self.extract_nodes_networkx()


    def extract_nodes_networkx(self) -> networkx.Graph:
        resource_nodes = [
            node
            for node, resource_type in self.graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
            if resource_type and resource_type in self.supported_resource_types
        ]

        return self.graph_connector.subgraph(resource_nodes)


    def extract_resource(self, supported_resources_graph: networkx.Graph) -> \
            Generator[dict[str, Any], dict[str, Any], dict[str, Any]]:
        def extract_resource_networkx(graph: networkx.Graph) -> Generator[dict[str, Any], None, None]:
            for _, resource in graph.nodes(data=True):
                yield resource

        graph_resource = None
        if self.graph_framework == 'NETWORKX':
            graph_resource = extract_resource_networkx(supported_resources_graph)

        return graph_resource  # type: ignore
