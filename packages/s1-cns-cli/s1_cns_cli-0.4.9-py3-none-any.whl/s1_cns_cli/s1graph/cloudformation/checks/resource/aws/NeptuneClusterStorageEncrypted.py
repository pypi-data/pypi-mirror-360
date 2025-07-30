from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class NeptuneClusterStorageEncrypted(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Neptune storage is securely encrypted"
        id = "CKV_AWS_44"
        supported_resources = ("AWS::Neptune::DBCluster",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/StorageEncrypted"


check = NeptuneClusterStorageEncrypted()
