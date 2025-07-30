from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SynapseWorkspaceEnablesDataExfilProtection(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Synapse workspace has data_exfiltration_protection_enabled"
        id = "CKV_AZURE_157"
        supported_resources = ['azurerm_synapse_workspace']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'data_exfiltration_protection_enabled'


check = SynapseWorkspaceEnablesDataExfilProtection()
