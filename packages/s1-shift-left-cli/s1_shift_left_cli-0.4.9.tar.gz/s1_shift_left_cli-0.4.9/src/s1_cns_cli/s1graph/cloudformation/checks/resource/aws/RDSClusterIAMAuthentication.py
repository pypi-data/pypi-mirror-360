from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RDSClusterIAMAuthentication(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure RDS cluster has IAM authentication enabled"
        id = "CKV_AWS_162"
        supported_resources = ["AWS::RDS::DBCluster"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/EnableIAMDatabaseAuthentication"


check = RDSClusterIAMAuthentication()
