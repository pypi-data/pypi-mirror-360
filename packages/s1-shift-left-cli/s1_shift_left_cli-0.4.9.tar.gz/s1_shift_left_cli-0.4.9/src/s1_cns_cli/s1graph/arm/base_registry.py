from __future__ import annotations

from typing import Any

from s1_cns_cli.s1graph.common.s1cns.check_type import CheckType
from s1_cns_cli.s1graph.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        super().__init__(report_type=CheckType.ARM)

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        resource_name, resource = next(iter(entity.items()))
        resource_type = str(resource.get("type", ""))  # entity['type'] ??
        return resource_type, resource_name, resource
