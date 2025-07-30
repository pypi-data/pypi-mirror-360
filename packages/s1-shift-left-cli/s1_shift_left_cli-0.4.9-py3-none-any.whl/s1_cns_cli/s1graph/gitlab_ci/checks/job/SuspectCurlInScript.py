from __future__ import annotations
from typing import Any
from s1_cns_cli.s1graph.common.models.enums import CheckResult

from s1_cns_cli.s1graph.gitlab_ci.checks.base_gitlab_ci_check import BaseGitlabCICheck
from s1_cns_cli.s1graph.yaml_doc.enums import BlockType


class SuspectCurlInScript(BaseGitlabCICheck):
    def __init__(self) -> None:
        name = "Suspicious use of curl with CI environment variables in script"
        id = "CKV_GITLABCI_1"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=('*.script[]',)
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        for line in conf.values():
            if not isinstance(line, str):
                continue
            if line.startswith("curl") and "$CI" in line:
                return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf


check = SuspectCurlInScript()
