from typing import Any

from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class EKSPublicAccess(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Amazon EKS public endpoint disabled"
        id = "CKV_AWS_39"
        supported_resources = ("aws_eks_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "vpc_config/[0]/endpoint_public_access"

    def get_expected_value(self) -> Any:
        return False


check = EKSPublicAccess()
