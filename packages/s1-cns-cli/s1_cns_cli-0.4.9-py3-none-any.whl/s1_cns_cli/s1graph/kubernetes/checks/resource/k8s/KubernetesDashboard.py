from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubernetesDashboard(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "Ensure the Kubernetes dashboard is not deployed"
        id = "CKV_K8S_33"
        # Location: container .image
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["image"]
        if conf.get("image"):
            conf_image = conf["image"]
            if not isinstance(conf_image, str):
                return CheckResult.FAILED
            if "kubernetes-dashboard" in conf_image or "kubernetesui" in conf_image:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        if metadata and metadata.get("labels"):
            if "app" in metadata["labels"]:
                if metadata["labels"]["app"] == "kubernetes-dashboard":
                    return CheckResult.FAILED
            elif "kubernetes-app" in metadata["labels"]:
                if metadata["labels"]["kubernetes-app"] == "kubernetes-dashboard":
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = KubernetesDashboard()
