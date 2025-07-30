from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleStoragePublicAccessPrevention(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure public access prevention is enforced on Cloud Storage bucket"
        id = "CKV_GCP_114"
        supported_resources = ["google_storage_bucket"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_access_prevention"

    def get_expected_value(self) -> Any:
        return "enforced"


check = GoogleStoragePublicAccessPrevention()
