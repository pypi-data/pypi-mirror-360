from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class ActionTrailLogAllRegions(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Action Trail Logging for all regions"
        id = "CKV_ALI_4"
        supported_resources = ("alicloud_actiontrail_trail",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.PASSED,
        )

    def get_inspected_key(self) -> str:
        return "trail_region"

    def get_expected_value(self) -> Any:
        return "All"


check = ActionTrailLogAllRegions()
