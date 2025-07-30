from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE


class StorageBlockEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "OCI Block Storage Block Volumes are not encrypted with a Customer Managed Key (CMK)"
        id = "CKV_OCI_3"
        supported_resources = ('oci_core_volume',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'kms_key_id'

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = StorageBlockEncryption()
