from typing import Any, Dict

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class SchedulerProfiling(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_114"
        name = "Ensure that the --profiling argument is set to false"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-scheduler" in conf["command"]:
                if "--profiling=false" not in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = SchedulerProfiling()
