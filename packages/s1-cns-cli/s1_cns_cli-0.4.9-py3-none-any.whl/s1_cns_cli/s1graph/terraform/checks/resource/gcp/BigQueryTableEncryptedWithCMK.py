from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class BigQueryTableEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Big Query Tables are encrypted with Customer Supplied Encryption Keys (CSEK)"
        id = "CKV_GCP_80"
        supported_resources = ['google_bigquery_table']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'encryption_configuration/[0]/kms_key_name'

    def get_expected_value(self):
        return ANY_VALUE


check = BigQueryTableEncryptedWithCMK()
