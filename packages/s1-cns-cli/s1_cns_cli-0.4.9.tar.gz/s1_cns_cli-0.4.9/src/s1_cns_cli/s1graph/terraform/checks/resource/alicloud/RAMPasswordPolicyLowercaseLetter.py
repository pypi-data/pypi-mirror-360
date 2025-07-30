from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PasswordPolicyLowercaseLetter(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RAM password policy requires at least one lowercase letter"
        id = "CKV_ALI_17"
        supported_resources = ['alicloud_ram_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'require_lowercase_characters'


check = PasswordPolicyLowercaseLetter()
