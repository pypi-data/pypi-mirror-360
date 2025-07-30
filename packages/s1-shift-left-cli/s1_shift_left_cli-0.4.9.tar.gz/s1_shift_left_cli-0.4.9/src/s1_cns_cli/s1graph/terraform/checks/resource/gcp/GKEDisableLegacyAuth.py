from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class GKEDisabledLegacyAuth(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Legacy Authorization is set to Disabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_7"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'enable_legacy_abac'

    def get_forbidden_values(self):
        return [True]


check = GKEDisabledLegacyAuth()
