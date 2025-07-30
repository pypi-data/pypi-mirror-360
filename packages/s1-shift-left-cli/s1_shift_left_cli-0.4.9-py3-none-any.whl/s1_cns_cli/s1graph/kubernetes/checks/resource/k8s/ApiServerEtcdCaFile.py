from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck
from s1_cns_cli.s1graph.kubernetes.checks.resource.k8s.k8s_check_utils import extract_commands


class ApiServerEtcdCaFile(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_102"
        name = "Ensure that the --etcd-cafile argument is set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        keys, values = extract_commands(conf)

        if "kube-apiserver" in keys:
            if "--etcd-cafile" not in keys:
                return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerEtcdCaFile()
