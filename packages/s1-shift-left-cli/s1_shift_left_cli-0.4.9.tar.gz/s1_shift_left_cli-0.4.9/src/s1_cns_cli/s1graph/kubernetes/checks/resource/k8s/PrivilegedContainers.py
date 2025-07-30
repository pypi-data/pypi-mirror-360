from typing import Any, Dict

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class PrivilegedContainers(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.3 1.7.1
        # CIS-1.5 5.2.1
        name = "Container should not be privileged"
        id = "CKV_K8S_16"
        # Location: container .securityContext.privileged
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["securityContext/privileged"]
        if conf.get("securityContext"):
            if conf["securityContext"].get("privileged"):
                return CheckResult.FAILED
        return CheckResult.PASSED


check = PrivilegedContainers()
