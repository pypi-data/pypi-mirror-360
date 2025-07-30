from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ECRImmutableTags(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure ECR Image Tags are immutable"
        id = "CKV_AWS_51"
        supported_resources = ("aws_ecr_repository",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "image_tag_mutability"

    def get_expected_value(self) -> Any:
        return "IMMUTABLE"


check = ECRImmutableTags()
