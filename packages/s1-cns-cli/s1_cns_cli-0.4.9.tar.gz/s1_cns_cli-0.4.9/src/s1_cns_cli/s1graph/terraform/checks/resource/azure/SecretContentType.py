from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE


class SecretContentType(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that key vault secrets have \"content_type\" set"
        id = "CKV_AZURE_114"
        supported_resources = ['azurerm_key_vault_secret']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'content_type'

    def get_expected_value(self):
        return ANY_VALUE


check = SecretContentType()
