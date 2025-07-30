from s1_cns_cli.s1graph.common.models.consts import ANY_VALUE
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories


class AppServiceHttpLoggingEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that App service enables HTTP logging"
        id = "CKV_AZURE_63"
        supported_resources = ('azurerm_app_service', 'azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "logs/[0]/http_logs"

    def get_expected_value(self):
        return ANY_VALUE


check = AppServiceHttpLoggingEnabled()
