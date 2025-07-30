from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerInsecurePort(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_88"
        name = "Ensure that the --insecure-port argument is set to 0"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-apiserver" in conf["command"]:
                if "--insecure-port=0" not in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerInsecurePort()
