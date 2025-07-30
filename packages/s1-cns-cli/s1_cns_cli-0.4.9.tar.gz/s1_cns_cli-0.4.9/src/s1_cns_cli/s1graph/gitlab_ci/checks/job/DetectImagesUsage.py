from __future__ import annotations

from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.gitlab_ci.checks.base_gitlab_ci_check import BaseGitlabCICheck
from s1_cns_cli.s1graph.yaml_doc.enums import BlockType


class DetectImageUsage(BaseGitlabCICheck):
    def __init__(self) -> None:
        name = "Detecting image usages in gitlab workflows"
        id = "CKV_GITLABCI_3"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=('*.image[]', '*.services[]')
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        return CheckResult.PASSED, conf


check = DetectImageUsage()
