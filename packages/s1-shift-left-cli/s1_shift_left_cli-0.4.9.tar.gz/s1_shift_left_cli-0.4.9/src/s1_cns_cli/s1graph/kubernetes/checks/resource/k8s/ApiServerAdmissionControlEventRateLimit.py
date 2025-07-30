from __future__ import annotations

from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_spec_check import BaseK8Check


class ApiServerAdmissionControlEventRateLimit(BaseK8Check):
    def __init__(self) -> None:
        id = "CKV_K8S_78"
        name = "Ensure that the admission control plugin EventRateLimit is set"
        categories = (CheckCategories.KUBERNETES,)
        supported_kind = ('AdmissionConfiguration',)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "plugins" not in conf:
            return CheckResult.FAILED
        plugins = conf["plugins"]
        for plugin in plugins:
            if plugin["name"] == "EventRateLimit":
                return CheckResult.PASSED

        return CheckResult.FAILED


check = ApiServerAdmissionControlEventRateLimit()
