from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class EKSSecretsEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure EKS Cluster has Secrets Encryption Enabled"
        id = "CKV_AWS_58"
        supported_resources = ['aws_eks_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encryption_config/[0]/resources"

    def get_expected_value(self):
        return ["secrets"]


check = EKSSecretsEncryption()
