from typing import Any

from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class DMSReplicationInstancePubliclyAccessible(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "DMS replication instance should not be publicly accessible"
        id = "CKV_AWS_89"
        supported_resources = ("AWS::DMS::ReplicationInstance",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/PubliclyAccessible"

    def get_expected_value(self) -> Any:
        return False


check = DMSReplicationInstancePubliclyAccessible()
