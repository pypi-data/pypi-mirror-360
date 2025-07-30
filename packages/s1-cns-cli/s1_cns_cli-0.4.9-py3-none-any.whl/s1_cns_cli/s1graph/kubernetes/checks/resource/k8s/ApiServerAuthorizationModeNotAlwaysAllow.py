from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerAuthorizationModeNotAlwaysAllow(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_74"
        name = "Ensure that the --authorization-mode argument is not set to AlwaysAllow"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith("--authorization-mode"):
                        modes = command.split("=")[1]
                        if "AlwaysAllow" in modes.split(","):
                            return CheckResult.FAILED
                        break

        return CheckResult.PASSED


check = ApiServerAuthorizationModeNotAlwaysAllow()
