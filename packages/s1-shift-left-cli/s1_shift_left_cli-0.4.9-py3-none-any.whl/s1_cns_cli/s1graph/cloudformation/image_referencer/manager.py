from __future__ import annotations

from typing import TYPE_CHECKING

from s1_cns_cli.s1graph.cloudformation.image_referencer.provider.aws import AwsCloudFormationProvider
from s1_cns_cli.s1graph.common.images.graph.image_referencer_manager import GraphImageReferencerManager

if TYPE_CHECKING:
    from s1_cns_cli.s1graph.common.images.image_referencer import Image


class CloudFormationImageReferencerManager(GraphImageReferencerManager):

    def extract_images_from_resources(self) -> list[Image]:
        aws_provider = AwsCloudFormationProvider(graph_connector=self.graph_connector)

        images = aws_provider.extract_images_from_resources()

        return images
