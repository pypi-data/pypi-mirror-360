from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class ELBAccessLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the ELB has access logging enabled"
        id = "CKV_AWS_92"
        supported_resources = ['AWS::ElasticLoadBalancing::LoadBalancer']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/AccessLoggingPolicy/Enabled'


check = ELBAccessLogs()
