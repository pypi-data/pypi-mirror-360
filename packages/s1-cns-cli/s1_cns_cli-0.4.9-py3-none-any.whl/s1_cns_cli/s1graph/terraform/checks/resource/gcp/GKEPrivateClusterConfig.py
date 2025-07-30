from typing import Any

from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE


class GKEPodSecurityPolicyEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Kubernetes Cluster is created with Private cluster enabled"
        id = "CKV_GCP_25"
        supported_resources = ("google_container_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "private_cluster_config"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = GKEPodSecurityPolicyEnabled()
