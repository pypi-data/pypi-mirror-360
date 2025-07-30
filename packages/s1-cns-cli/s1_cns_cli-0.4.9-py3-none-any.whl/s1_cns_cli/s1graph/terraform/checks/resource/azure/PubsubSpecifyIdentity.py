from typing import Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE


class PubsubSpecifyIdentity(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Web PubSub uses managed identities to access Azure resources"
        id = "CKV_AZURE_176"
        supported_resources = ("azurerm_web_pubsub",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "identity/[0]/type"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = PubsubSpecifyIdentity()
