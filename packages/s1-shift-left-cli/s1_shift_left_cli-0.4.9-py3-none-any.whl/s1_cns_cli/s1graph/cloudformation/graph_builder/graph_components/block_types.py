from dataclasses import dataclass

from s1_cns_cli.s1graph.common.graph.graph_builder.graph_components.block_types import BlockType as CommonBlockType


@dataclass
class BlockType(CommonBlockType):
    METADATA = "metadata"
    PARAMETERS = "parameters"
    RULES = "rules"
    MAPPINGS = "mappings"
    CONDITIONS = "conditions"
    TRANSFORM = "transform"
    OUTPUTS = "outputs"
    GLOBALS = "globals"
