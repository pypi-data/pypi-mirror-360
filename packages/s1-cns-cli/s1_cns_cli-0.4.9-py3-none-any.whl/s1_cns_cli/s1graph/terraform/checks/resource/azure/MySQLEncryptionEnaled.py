from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MySQLEncryptionEnaled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that MySQL server enables infrastructure encryption"
        id = "CKV_AZURE_96"
        supported_resources = ['azurerm_mysql_server']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'infrastructure_encryption_enabled'


check = MySQLEncryptionEnaled()
