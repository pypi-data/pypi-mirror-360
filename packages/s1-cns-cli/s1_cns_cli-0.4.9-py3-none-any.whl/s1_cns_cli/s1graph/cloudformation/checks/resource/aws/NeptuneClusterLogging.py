from __future__ import annotations

from typing import Any

from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories


class NeptuneClusterLogging(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Neptune logging is enabled"
        id = "CKV_AWS_101"
        supported_resources = ("AWS::Neptune::DBCluster",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        logs_exports = conf.get("Properties", {}).get("EnableCloudwatchLogsExports", [])
        if "audit" in logs_exports:
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["Properties/EnableCloudwatchLogsExports"]


check = NeptuneClusterLogging()
