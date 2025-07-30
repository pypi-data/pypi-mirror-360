from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class RDSDeletionProtection(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that RDS clusters have deletion protection enabled"
        id = "CKV_AWS_139"
        supported_resources = ['aws_rds_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'deletion_protection'


check = RDSDeletionProtection()
