from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any

from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE


class DropletSSHKeys(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the droplet specifies an SSH key"
        id = "CKV_DIO_2"
        supported_resources = ['digitalocean_droplet']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "ssh_keys"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = DropletSSHKeys()
