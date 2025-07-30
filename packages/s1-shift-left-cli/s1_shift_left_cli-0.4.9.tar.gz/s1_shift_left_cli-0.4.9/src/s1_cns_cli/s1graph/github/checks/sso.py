from __future__ import annotations

from typing import Any

from bc_jsonpath_ng import parse

from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories
from s1_cns_cli.s1graph.github.base_github_configuration_check import BaseGithubCheck
from s1_cns_cli.s1graph.github.schemas.org_security import schema as org_security_schema
from s1_cns_cli.s1graph.json_doc.enums import BlockType


class GithubSSO(BaseGithubCheck):
    def __init__(self) -> None:
        name = "Ensure GitHub organization security settings require SSO"
        id = "CKV_GITHUB_2"
        categories = (CheckCategories.SUPPLY_CHAIN, )
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:  # type:ignore[override]
        if org_security_schema.validate(conf):
            jsonpath_expression = parse("$..{}".format(self.get_evaluated_keys()[0].replace("/", ".")))
            if len(jsonpath_expression.find(conf)) > 0:
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> list[str]:
        return ['data/organization/samlIdentityProvider/ssoUrl']


check = GithubSSO()
