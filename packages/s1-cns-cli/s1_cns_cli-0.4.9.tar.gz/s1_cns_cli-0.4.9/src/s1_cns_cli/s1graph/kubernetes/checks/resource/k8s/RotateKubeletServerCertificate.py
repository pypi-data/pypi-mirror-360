from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


COMPONENT_TYPES = ("kube-controller-manager", "kubelet")


class RotateKubeletServerCertificate(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.12
        id = "CKV_K8S_112"
        name = "Ensure that the RotateKubeletServerCertificate argument is set to true"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        command = conf.get("command")
        if isinstance(command, list) and any(item in command for item in COMPONENT_TYPES):
            for idx, cmd in enumerate(command):
                self.evaluated_container_keys = [f"command/[{idx}]"]
                if cmd.startswith("--feature-gates") and "RotateKubeletServerCertificate=false" in cmd:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = RotateKubeletServerCertificate()
