from __future__ import annotations

from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_check import BaseResourceCheck


class VPCDefaultNetwork(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure no default VPC is planned to be provisioned"
        id = "CKV_AWS_148"
        supported_resources = ("aws_default_vpc",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        """
            Checks if there is any attempt to create a default VPC configuration :
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/default_vpc
            :param conf: aws_default_vpc configuration
            :return: <CheckResult>
        """
        return CheckResult.FAILED


check = VPCDefaultNetwork()
