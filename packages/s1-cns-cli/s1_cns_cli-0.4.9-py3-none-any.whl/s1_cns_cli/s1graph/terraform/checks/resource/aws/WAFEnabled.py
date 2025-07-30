from typing import List, Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class WAFEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "CloudFront Distribution should have WAF enabled"
        id = "CKV_AWS_68"
        supported_resources = ["aws_cloudfront_distribution"]
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "web_acl_id"

    def get_expected_values(self) -> List[Any]:
        return [ANY_VALUE]


check = WAFEnabled()
