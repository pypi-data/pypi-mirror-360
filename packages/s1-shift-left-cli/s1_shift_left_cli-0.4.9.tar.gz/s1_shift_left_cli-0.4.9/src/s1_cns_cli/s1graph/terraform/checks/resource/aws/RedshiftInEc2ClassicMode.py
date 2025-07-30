from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RedshiftInEc2ClassicMode(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Redshift is not deployed outside of a VPC"
        id = "CKV_AWS_154"
        supported_resources = ['aws_redshift_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "cluster_subnet_group_name"

    def get_expected_value(self):
        return ANY_VALUE


check = RedshiftInEc2ClassicMode()
