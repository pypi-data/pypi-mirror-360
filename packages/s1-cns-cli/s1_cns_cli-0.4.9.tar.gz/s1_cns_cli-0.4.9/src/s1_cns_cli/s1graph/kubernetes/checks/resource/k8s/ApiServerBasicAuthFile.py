from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerBasicAuthFile(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_69"
        name = "Ensure that the --basic-config-file argument is not set"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        command = conf.get("command")
        if isinstance(command, list):
            if "kube-apiserver" in command:
                if any(x.startswith("--basic-config-file") for x in command):
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerBasicAuthFile()
