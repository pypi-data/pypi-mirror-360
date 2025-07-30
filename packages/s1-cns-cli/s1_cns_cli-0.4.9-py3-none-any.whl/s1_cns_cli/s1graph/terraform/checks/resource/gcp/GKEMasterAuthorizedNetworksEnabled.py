from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE


class GKEMasterAuthorizedNetworksEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure master authorized networks is set to enabled in GKE clusters"
        id = "CKV_GCP_20"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'master_authorized_networks_config'

    def get_expected_values(self):
        return [ANY_VALUE]


check = GKEMasterAuthorizedNetworksEnabled()
