from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class NetworkIPsecProtocols(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure IPsec profiles do not specify use of insecure protocols"
        id = "CKV_PAN_13"
        supported_resources = ['panos_ipsec_crypto_profile', 'panos_panorama_ipsec_crypto_profile']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'protocol'

    def get_forbidden_values(self):
        return ['ah']


check = NetworkIPsecProtocols()
