from typing import Any

from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class LambdaInVPC(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that AWS Lambda function is configured inside a VPC"
        id = "CKV_AWS_117"
        supported_resources = ("AWS::Lambda::Function", "AWS::Serverless::Function")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/VpcConfig"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = LambdaInVPC()
