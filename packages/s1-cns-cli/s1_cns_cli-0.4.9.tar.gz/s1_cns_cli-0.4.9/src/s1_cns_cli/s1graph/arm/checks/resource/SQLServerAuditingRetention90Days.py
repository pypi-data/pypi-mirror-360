from typing import Dict, Any

from s1_cns_cli.s1graph.arm.base_resource_check import BaseResourceCheck
from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories
from s1_cns_cli.s1graph.common.util.type_forcers import force_list

# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2019-06-01-preview/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2017-03-01-preview/servers/databases/auditingsettings


class SQLServerAuditingRetention90Days(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Auditing' Retention is 'greater than 90 days' for SQL servers"
        id = "CKV_AZURE_24"
        supported_resources = ("Microsoft.Sql/servers",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["resources"]
        resources = conf.get("resources") or []
        for idx, resource in enumerate(force_list(resources)):
            self.evaluated_keys = [
                f"resources/[{idx}]/type",
                f"resources/[{idx}]/properties/state",
                f"resources/[{idx}]/properties/retentionDays",
            ]
            if resource.get("type") in (
                "Microsoft.Sql/servers/databases/auditingSettings",
                "auditingSettings",
            ):
                properties = resource.get("properties")
                if isinstance(properties, dict):
                    state = properties.get("state")
                    if isinstance(state, str) and state.lower() == "enabled":
                        retention = properties.get("retentionDays")
                        if isinstance(retention, int) and retention >= 90:
                            return CheckResult.PASSED

        return CheckResult.FAILED


check = SQLServerAuditingRetention90Days()
