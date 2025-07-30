from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class InstanceBootVolumeIntransitEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure OCI Compute Instance boot volume has in-transit data encryption enabled"
        id = "CKV_OCI_4"
        supported_resources = ['oci_core_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "launch_options/[0]/is_pv_encryption_in_transit_enabled"

    def get_expected_value(self):
        return True


check = InstanceBootVolumeIntransitEncryption()
