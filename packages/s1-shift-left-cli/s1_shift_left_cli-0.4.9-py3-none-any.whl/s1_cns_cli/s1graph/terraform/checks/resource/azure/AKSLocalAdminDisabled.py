from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AKSLocalAdminDisabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure AKS local admin account is disabled"
        id = "CKV_AZURE_141"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "local_account_disabled"

    def get_expected_value(self):
        return True


check = AKSLocalAdminDisabled()
