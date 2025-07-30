from typing import Dict, List, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories
from s1_cns_cli.s1graph.terraform.checks.provider.base_check import BaseProviderCheck


class OciCredentials(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure no hard coded OCI private key in provider"
        id = "CKV_OCI_1"
        supported_provider = ["oci"]
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        key = "private_key_password"
        if key in conf.keys():
            secret = conf[key]
            if not secret:
                return CheckResult.PASSED
            conf[f'{self.id}_secret'] = secret
            return CheckResult.FAILED
        else:
            return CheckResult.PASSED


check = OciCredentials()
