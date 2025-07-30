from abc import abstractmethod
from collections.abc import Iterable
from typing import List, Dict, Any, Optional

from s1_cns_cli.s1graph.common.checks.base_check import BaseCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.terraform.checks.provider.registry import provider_registry


class BaseProviderCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_provider: "Iterable[str]",
        guideline: Optional[str] = None
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_provider,
            block_type="provider",
            guideline=guideline,
        )
        self.supported_provider = supported_provider
        provider_registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        return self.scan_provider_conf(conf)

    @abstractmethod
    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        raise NotImplementedError()
