from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerTokenAuthFile(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_70"
        name = "Ensure that the --token-config-file argument is not set"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-apiserver" in conf["command"]:
                if any(x.startswith("--token-config-file") for x in conf["command"]):
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerTokenAuthFile()
