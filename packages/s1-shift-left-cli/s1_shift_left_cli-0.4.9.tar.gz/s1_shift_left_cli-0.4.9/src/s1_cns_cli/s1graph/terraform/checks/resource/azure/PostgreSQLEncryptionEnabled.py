from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PostgreSQLEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that PostgreSQL server enables infrastructure encryption"
        id = "CKV_AZURE_130"
        supported_resources = ("azurerm_postgresql_server",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "infrastructure_encryption_enabled"


check = PostgreSQLEncryptionEnabled()
