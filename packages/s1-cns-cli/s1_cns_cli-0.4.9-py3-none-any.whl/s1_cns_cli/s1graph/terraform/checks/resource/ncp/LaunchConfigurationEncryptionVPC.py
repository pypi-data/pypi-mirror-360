from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LaunchConfigurationEncryptionVPC(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Basic Block storage is encrypted."
        id = "CKV_NCP_7"
        supported_resources = ("ncloud_launch_configuration",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "is_encrypted_volume"


check = LaunchConfigurationEncryptionVPC()
