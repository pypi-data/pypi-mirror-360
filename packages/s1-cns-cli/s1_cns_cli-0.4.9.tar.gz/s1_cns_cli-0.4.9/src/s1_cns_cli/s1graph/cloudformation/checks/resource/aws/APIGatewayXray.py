from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class APIGatewayXray(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure API Gateway has X-Ray Tracing enabled"
        id = "CKV_AWS_73"
        supported_resources = ['AWS::ApiGateway::Stage', "AWS::Serverless::Api"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/TracingEnabled'

    def get_expected_value(self):
        return True


check = APIGatewayXray()
