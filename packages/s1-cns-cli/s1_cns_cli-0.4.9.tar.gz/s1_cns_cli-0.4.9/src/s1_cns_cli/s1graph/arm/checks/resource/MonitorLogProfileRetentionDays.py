from __future__ import annotations

from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories
from s1_cns_cli.s1graph.arm.base_resource_check import BaseResourceCheck
from s1_cns_cli.s1graph.common.util.type_forcers import force_int

# https://docs.microsoft.com/en-us/azure/templates/microsoft.insights/2016-03-01/logprofiles


class MonitorLogProfileRetentionDays(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Activity Log Retention is set 365 days or greater"
        id = "CKV_AZURE_37"
        supported_resources = ("Microsoft.Insights/logprofiles",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "properties" in conf and "retentionPolicy" in conf["properties"]:
            retention = conf["properties"]["retentionPolicy"]
            if "enabled" in retention and str(retention["enabled"]).lower() == "true":
                if "days" in retention:
                    days = force_int(retention["days"])
                    if days is not None and (days == 0 or days >= 365):
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = MonitorLogProfileRetentionDays()
