from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class VPCEndpointAcceptanceConfigured(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that VPC Endpoint Service is configured for Manual Acceptance"
        id = "CKV_AWS_123"
        supported_resources = ['aws_vpc_endpoint_service']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'acceptance_required'


check = VPCEndpointAcceptanceConfigured()
