from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class NeptuneClusterStorageEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Neptune storage is securely encrypted"
        id = "CKV_AWS_44"
        supported_resources = ['aws_neptune_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "storage_encrypted"


check = NeptuneClusterStorageEncrypted()
