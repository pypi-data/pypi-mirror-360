from __future__ import annotations

from typing import Any
from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories
from s1_cns_cli.s1graph.common.checks.enums import BlockType
from s1_cns_cli.s1graph.openapi.checks.base_openapi_check import BaseOpenapiCheck


class GlobalSecurityFieldIsEmpty(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_4"
        name = "Ensure that the global security field has rules defined"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['security']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:  # type:ignore[override]  # return type is different than the base class
        security_rules = conf.get("security")

        if security_rules:
            return CheckResult.PASSED, security_rules
        return CheckResult.FAILED, conf


check = GlobalSecurityFieldIsEmpty()
