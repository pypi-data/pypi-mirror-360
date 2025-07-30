from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class APIGatewayXray(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure API Gateway has X-Ray Tracing enabled"
        id = "CKV_AWS_73"
        supported_resources = ['aws_api_gateway_stage']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "xray_tracing_enabled"


check = APIGatewayXray()
