from __future__ import annotations

from s1_cns_cli.s1graph.ansible.checks.base_ansible_task_value_check import BaseAnsibleTaskValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories


class GetUrlValidateCerts(BaseAnsibleTaskValueCheck):
    def __init__(self) -> None:
        name = "Ensure that certificate validation isn't disabled with get_url"
        id = "CKV_ANSIBLE_2"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("ansible.builtin.get_url", "get_url"),
            missing_block_result=CheckResult.PASSED,
        )

    def get_inspected_key(self) -> str:
        return "validate_certs"


check = GetUrlValidateCerts()
