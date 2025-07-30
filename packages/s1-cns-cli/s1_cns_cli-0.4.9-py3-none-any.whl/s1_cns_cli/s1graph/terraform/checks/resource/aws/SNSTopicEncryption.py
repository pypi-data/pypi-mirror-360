from typing import List, Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SNSTopicEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the SNS topic is encrypted"
        id = "CKV_AWS_26"
        supported_resources = ("aws_sns_topic",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "kms_master_key_id"

    def get_expected_values(self) -> List[Any]:
        return [ANY_VALUE]


check = SNSTopicEncryption()
