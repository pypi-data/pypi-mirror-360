from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class ImagebuilderDistributionConfigurationEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Image Builder Distribution Configuration encrypts AMI's " \
               "using KMS - a customer managed Key (CMK)"
        id = "CKV_AWS_199"
        supported_resources = ['aws_imagebuilder_distribution_configuration']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "distribution/[0]/ami_distribution_configuration/[0]/kms_key_id"

    def get_expected_value(self) -> str:
        return ANY_VALUE


check = ImagebuilderDistributionConfigurationEncryptedWithCMK()
