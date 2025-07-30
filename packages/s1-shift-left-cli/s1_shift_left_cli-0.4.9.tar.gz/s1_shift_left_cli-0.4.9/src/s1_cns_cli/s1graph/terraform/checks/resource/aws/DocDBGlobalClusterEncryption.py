from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DocDBGlobalClusterEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DocDB Global Cluster is encrypted at rest (default is unencrypted)"
        id = "CKV_AWS_292"
        supported_resources = ('aws_docdb_global_cluster',)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "storage_encrypted"


check = DocDBGlobalClusterEncryption()
