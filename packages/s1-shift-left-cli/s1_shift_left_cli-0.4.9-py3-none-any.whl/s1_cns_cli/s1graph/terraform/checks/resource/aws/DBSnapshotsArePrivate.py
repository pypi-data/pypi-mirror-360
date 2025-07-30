

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class BDSnapshotsArePrivate(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure DB Snapshots are not Public"
        id = "CKV_AWS_302"
        supported_resources = ['aws_db_snapshot']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "shared_accounts"

    def get_forbidden_values(self):
        return ["all"]


check = BDSnapshotsArePrivate()
