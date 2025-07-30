from typing import List, Any

from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class DocDBTLS(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure DocDB TLS is not disabled"
        id = "CKV_AWS_90"
        supported_resources = ['AWS::DocDB::DBClusterParameterGroup']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/Parameters/tls"

    def get_forbidden_values(self) -> List[Any]:
        return ["disabled"]


check = DocDBTLS()
