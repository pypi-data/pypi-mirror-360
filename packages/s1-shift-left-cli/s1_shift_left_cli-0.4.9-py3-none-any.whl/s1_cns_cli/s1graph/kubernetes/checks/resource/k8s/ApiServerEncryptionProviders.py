from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck
from s1_cns_cli.s1graph.kubernetes.checks.resource.k8s.k8s_check_utils import extract_commands


class ApiServerEncryptionProviders(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_104"
        name = "Ensure that encryption providers are appropriately configured"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        keys, values = extract_commands(conf)

        if "kube-apiserver" in keys:
            if "--encryption-provider-config" not in keys:
                return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerEncryptionProviders()
