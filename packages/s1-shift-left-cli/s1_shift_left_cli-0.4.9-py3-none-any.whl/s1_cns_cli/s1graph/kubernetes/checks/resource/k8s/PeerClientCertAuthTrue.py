from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_spec_check import BaseK8Check


class PeerClientCertAuthTrue(BaseK8Check):

    def __init__(self):
        name = "Ensure that the --peer-client-cert-config argument is set to true"
        id = "CKV_K8S_121"
        supported_kind = ['Pod']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf, entity_type=None):
        if conf.get("metadata", {}).get('name') == 'etcd':
            containers = conf.get('spec')['containers']
            for container in containers:
                if container.get("args") is not None:
                    if '--peer-client-cert-config=true' not in container['args']:
                        return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = PeerClientCertAuthTrue()
