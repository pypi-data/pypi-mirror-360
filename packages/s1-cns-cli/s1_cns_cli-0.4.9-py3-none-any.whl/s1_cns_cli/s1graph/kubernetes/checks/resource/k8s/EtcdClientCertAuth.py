from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class EtcdClientCertAuth(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 2.2
        id = "CKV_K8S_117"
        name = "Ensure that the --client-cert-config argument is set to true"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        command = conf.get("command")
        if isinstance(command, list):
            if "etcd" in command and "--client-cert-config=true" not in command:
                return CheckResult.FAILED

        return CheckResult.PASSED


check = EtcdClientCertAuth()
