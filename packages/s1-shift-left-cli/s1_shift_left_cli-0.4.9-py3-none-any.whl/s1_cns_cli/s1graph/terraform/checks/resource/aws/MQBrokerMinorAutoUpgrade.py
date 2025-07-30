from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class MQBrokerMinorAutoUpgrade(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure MQ Broker minor version updates are enabled"
        id = "CKV_AWS_207"
        supported_resources = ['aws_mq_broker']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "auto_minor_version_upgrade"


check = MQBrokerMinorAutoUpgrade()
