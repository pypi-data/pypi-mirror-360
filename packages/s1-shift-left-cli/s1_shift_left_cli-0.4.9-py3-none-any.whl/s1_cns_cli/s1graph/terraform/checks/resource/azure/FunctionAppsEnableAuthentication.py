from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class FunctionAppsEnableAuthentication(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that function apps enables Authentication"
        id = "CKV_AZURE_56"
        supported_resources = ['azurerm_function_app']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'auth_settings/[0]/enabled'


check = FunctionAppsEnableAuthentication()
