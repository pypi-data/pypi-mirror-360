from __future__ import annotations

from typing import Any

from s1_cns_cli.s1graph.ansible.checks.base_ansible_task_value_check import BaseAnsibleTaskValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories


class AptAllowUnauthenticated(BaseAnsibleTaskValueCheck):
    def __init__(self) -> None:
        name = "Ensure that packages with untrusted or missing signatures are not used"
        id = "CKV_ANSIBLE_5"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("ansible.builtin.apt", "apt"),
            missing_block_result=CheckResult.PASSED,
        )

    def get_expected_value(self) -> Any:
        return False

    def get_inspected_key(self) -> str:
        return "allow_unauthenticated"


check = AptAllowUnauthenticated()
