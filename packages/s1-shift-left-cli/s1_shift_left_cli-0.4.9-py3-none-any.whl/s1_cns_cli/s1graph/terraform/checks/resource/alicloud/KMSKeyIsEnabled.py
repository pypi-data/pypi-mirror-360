from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class KMSKeyIsEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure KMS Keys are enabled"
        id = "CKV_ALI_28"
        supported_resources = ['alicloud_kms_key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "status"

    def get_expected_value(self) -> Any:
        return "Enabled"


check = KMSKeyIsEnabled()
