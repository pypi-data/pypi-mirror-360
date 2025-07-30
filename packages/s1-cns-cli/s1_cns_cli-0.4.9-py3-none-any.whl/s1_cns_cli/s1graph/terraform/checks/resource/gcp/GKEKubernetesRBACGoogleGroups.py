from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE


class GKEKubernetesRBACGoogleGroups(BaseResourceValueCheck):
    def __init__(self):
        name = "Manage Kubernetes RBAC users with Google Groups for GKE"
        id = "CKV_GCP_65"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'authenticator_groups_config/[0]/security_group'

    def get_expected_values(self):
        return [ANY_VALUE]


check = GKEKubernetesRBACGoogleGroups()
