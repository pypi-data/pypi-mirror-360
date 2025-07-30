from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class EFSEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure EFS is securely encrypted"
        id = "CKV_AWS_42"
        supported_resources = ['AWS::EFS::FileSystem']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/Encrypted'


check = EFSEncryption()
