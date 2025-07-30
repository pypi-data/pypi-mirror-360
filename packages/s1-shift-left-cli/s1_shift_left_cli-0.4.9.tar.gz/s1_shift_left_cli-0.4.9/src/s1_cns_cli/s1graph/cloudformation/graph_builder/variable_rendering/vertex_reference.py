from __future__ import annotations

from s1_cns_cli.s1graph.common.graph.graph_builder.variable_rendering.vertex_reference import VertexReference
from s1_cns_cli.s1graph.cloudformation.graph_builder.graph_components.block_types import BlockType


class CloudformationVertexReference(VertexReference):
    def __init__(self, block_type: str, sub_parts: list[str], origin_value: str) -> None:
        super().__init__(block_type, sub_parts, origin_value)

    @staticmethod
    def block_type_str_to_enum(block_type_str: str) -> str:
        return BlockType().get(block_type_str)
