from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MWAASchedulerLogsEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure MWAA environment has scheduler logs enabled"
        id = "CKV_AWS_242"
        supported_resources = ["aws_mwaa_environment"]
        categories = [CheckCategories.LOGGING]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "logging_configuration/[0]/scheduler_logs/[0]/enabled"


check = MWAASchedulerLogsEnabled()
