from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureDataExplorerDoubleEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Data Explorer uses double encryption"
        id = "CKV_AZURE_75"
        supported_resources = ['azurerm_kusto_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "double_encryption_enabled"

    def get_expected_value(self):
        return True


check = AzureDataExplorerDoubleEncryptionEnabled()
