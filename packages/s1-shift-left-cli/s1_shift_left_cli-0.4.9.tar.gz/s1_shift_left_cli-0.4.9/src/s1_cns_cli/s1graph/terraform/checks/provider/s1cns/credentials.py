import re
from typing import Dict, List, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories
from s1_cns_cli.s1graph.terraform.checks.provider.base_check import BaseProviderCheck
from s1_cns_cli.s1graph.common.models.consts import s1cns_token_pattern


class SentinelOneCnsCredentials(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure no hard coded API token exist in the provider"
        id = "CKV_BCW_1"
        supported_provider = ("s1cns",)
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if self.secret_found(conf, "token", s1cns_token_pattern):
            return CheckResult.FAILED
        return CheckResult.PASSED

    def secret_found(self, conf: Dict[str, List[Any]], field: str, pattern: str) -> bool:
        if field in conf.keys():
            value = conf[field][0]
            if re.match(pattern, value) is not None:
                conf[f'{self.id}_secret'] = value
                return True
        return False


check = SentinelOneCnsCredentials()
