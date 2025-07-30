from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ECRRepositoryEncrypted(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that ECR repositories are encrypted using KMS"
        id = "CKV_AWS_136"
        supported_resources = ("AWS::ECR::Repository",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/EncryptionConfiguration/EncryptionType"

    def get_expected_value(self) -> Any:
        return "KMS"


check = ECRRepositoryEncrypted()
