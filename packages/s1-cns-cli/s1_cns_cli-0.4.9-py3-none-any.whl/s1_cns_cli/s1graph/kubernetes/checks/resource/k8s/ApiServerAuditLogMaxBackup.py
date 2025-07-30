from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerAuditLogMaxBackup(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_93"
        name = "Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasAuditLogMaxBackup = False
                for command in conf["command"]:
                    if command.startswith("--audit-log-maxbackup"):
                        value = command.split("=")[1]
                        hasAuditLogMaxBackup = int(value) >= 10
                        break
                return CheckResult.PASSED if hasAuditLogMaxBackup else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerAuditLogMaxBackup()
