from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class EBSDefaultEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure EBS default encryption is enabled"
        id = "CKV_AWS_106"
        supported_resources = ("aws_ebs_encryption_by_default",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.PASSED,
        )

    def get_inspected_key(self) -> str:
        return "enabled"


check = EBSDefaultEncryption()
