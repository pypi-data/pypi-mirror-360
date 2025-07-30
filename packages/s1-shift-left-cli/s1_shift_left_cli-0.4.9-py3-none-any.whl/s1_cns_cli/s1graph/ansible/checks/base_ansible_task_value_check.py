from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from s1_cns_cli.s1graph.ansible.checks.base_ansible_task_check import BaseAnsibleTaskCheck
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.common.util.data_structures_utils import find_in_dict
from s1_cns_cli.s1graph.yaml_doc.enums import BlockType

if TYPE_CHECKING:
    from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class BaseAnsibleTaskValueCheck(BaseAnsibleTaskCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_modules: Iterable[str],
        guideline: str | None = None,
        path: str | None = None,
        missing_block_result: CheckResult = CheckResult.FAILED,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_modules=supported_modules,
            block_type=BlockType.ARRAY,
            guideline=guideline,
            path=path,
        )
        self.missing_block_result = missing_block_result

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        inspected_key = self.get_inspected_key()
        expected_values = self.get_expected_values()

        value = find_in_dict(conf, inspected_key)

        if value is None:
            return self.missing_block_result, self.entity_conf
        if ANY_VALUE in expected_values:
            return CheckResult.PASSED, self.entity_conf
        if value in expected_values:
            return CheckResult.PASSED, self.entity_conf
        # quite often string values are case-insensitive
        if isinstance(value, str) and value.lower() in [exp.lower() for exp in expected_values if isinstance(exp, str)]:
            return CheckResult.PASSED, self.entity_conf

        return CheckResult.FAILED, self.entity_conf

    @abstractmethod
    def get_inspected_key(self) -> str:
        """
        :return: JSONPath syntax path of the checked attribute
        """
        raise NotImplementedError()

    def get_expected_values(self) -> list[Any]:
        """
        Override the method with the list of acceptable values if the check has more than one possible expected value, given
        the inspected key
        :return: List of expected values, defaults to a list of the expected value
        """
        return [self.get_expected_value()]

    def get_expected_value(self) -> Any:
        """
        Returns the default expected value, governed by provider best practices
        """
        return True

    def get_evaluated_keys(self) -> list[str]:
        return [self.get_inspected_key()]
