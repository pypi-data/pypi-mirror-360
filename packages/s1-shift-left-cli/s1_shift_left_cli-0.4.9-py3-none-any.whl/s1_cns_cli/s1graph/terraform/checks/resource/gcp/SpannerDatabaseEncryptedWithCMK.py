from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class SpannerDatabaseEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Spanner Database is encrypted with Customer Supplied Encryption Keys (CSEK)"
        id = "CKV_GCP_93"
        supported_resources = ['google_spanner_database']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'encryption_config/[0]/kms_key_name'

    def get_expected_value(self):
        return ANY_VALUE


check = SpannerDatabaseEncryptedWithCMK()
