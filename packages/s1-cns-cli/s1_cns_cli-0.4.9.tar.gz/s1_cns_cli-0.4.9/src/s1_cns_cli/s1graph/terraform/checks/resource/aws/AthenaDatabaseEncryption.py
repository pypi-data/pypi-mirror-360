from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AthenaDatabaseEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Athena Database is encrypted at rest (default is unencrypted)"
        id = "CKV_AWS_77"
        supported_resources = ['aws_athena_database']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encryption_configuration/[0]/encryption_option"

    def get_expected_value(self):
        return ANY_VALUE


check = AthenaDatabaseEncryption()
