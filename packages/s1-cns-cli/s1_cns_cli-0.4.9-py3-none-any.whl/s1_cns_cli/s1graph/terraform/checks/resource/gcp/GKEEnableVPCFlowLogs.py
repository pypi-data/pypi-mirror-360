from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GKEEnableVPCFlowLogs(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Enable VPC Flow Logs and Intranode Visibility"
        id = "CKV_GCP_61"
        supported_resources = ('google_container_cluster',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'enable_intranode_visibility'

    def get_expected_value(self) -> Any:
        return True


check = GKEEnableVPCFlowLogs()
