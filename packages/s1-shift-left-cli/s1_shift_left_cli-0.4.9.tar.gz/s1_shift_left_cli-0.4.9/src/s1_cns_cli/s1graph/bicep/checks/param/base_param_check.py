from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING

from pycep.typing import ParameterAttributes

from s1_cns_cli.s1graph.bicep.checks.param.registry import registry
from s1_cns_cli.s1graph.common.checks.base_check import BaseCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class SentinelOneCnsParameterAttributes(ParameterAttributes):
    CKV_AZURE_131_secret: NotRequired[str]  # noqa


class BaseParamCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_type: "Iterable[str]",
        guideline: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_type,
            block_type="param",
            guideline=guideline,
        )
        self.supported_type = supported_type
        registry.register(self)

    def scan_entity_conf(self, conf: SentinelOneCnsParameterAttributes, entity_type: str) -> CheckResult:  # type:ignore[override]  # it's ok
        self.entity_type = entity_type

        return self.scan_param_conf(conf)

    @abstractmethod
    def scan_param_conf(self, conf: SentinelOneCnsParameterAttributes) -> CheckResult:
        raise NotImplementedError()
