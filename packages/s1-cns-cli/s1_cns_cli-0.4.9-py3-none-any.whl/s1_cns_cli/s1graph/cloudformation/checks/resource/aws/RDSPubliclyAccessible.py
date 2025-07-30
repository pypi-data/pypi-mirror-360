from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories


class RDSPubliclyAccessible(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure all data stored in RDS is not publicly accessible"
        id = "CKV_AWS_17"
        supported_resources = ['AWS::RDS::DBInstance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_expected_value(self):
        return False

    def get_inspected_key(self):
        return 'Properties/PubliclyAccessible'


check = RDSPubliclyAccessible()
