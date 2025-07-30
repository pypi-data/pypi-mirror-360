from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class DataflowJobEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure data flow jobs are encrypted with Customer Supplied Encryption Keys (CSEK)"
        id = "CKV_GCP_90"
        supported_resources = ['google_dataflow_job']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_key_name'

    def get_expected_value(self):
        return ANY_VALUE


check = DataflowJobEncryptedWithCMK()
