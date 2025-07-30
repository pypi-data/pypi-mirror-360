from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AthenaWorkgroupConfiguration(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Athena Workgroup should enforce configuration to prevent client disabling encryption"
        id = "CKV_AWS_82"
        supported_resources = ("AWS::Athena::WorkGroup",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/WorkGroupConfiguration/EnforceWorkGroupConfiguration"


check = AthenaWorkgroupConfiguration()
