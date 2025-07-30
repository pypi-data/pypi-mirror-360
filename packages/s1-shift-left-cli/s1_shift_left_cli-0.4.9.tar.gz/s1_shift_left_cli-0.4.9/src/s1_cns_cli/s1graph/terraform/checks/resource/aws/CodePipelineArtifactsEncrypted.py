from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE


class CodePipelineArtifactsEncrypted(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Code Pipeline Artifact store is using a KMS CMK"
        id = "CKV_AWS_219"
        supported_resources = ("aws_codepipeline",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "artifact_store/[0]/encryption_key/[0]/id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = CodePipelineArtifactsEncrypted()
